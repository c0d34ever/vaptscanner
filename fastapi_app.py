from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import uvicorn
import asyncio
import json
import csv
import io
from datetime import datetime, timedelta
import os
import sys

# Add Django project to path for model access
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vapt_platform.settings')

import django
django.setup()

from scans.models import Scan, Finding, ScanLog, ScanTemplate, ScheduledScan
from scans.tasks import run_vapt_scan

# Import configuration
from env_config import settings

app = FastAPI(
    title="VAPT Scanner API",
    description="Vulnerability Assessment and Penetration Testing API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware with environment-based configuration
if settings.CORS_ALLOW_ALL:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    allowed_origins = [origin.strip() for origin in settings.CORS_ALLOWED_ORIGINS.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models
class ScanCreate(BaseModel):
    target_url: HttpUrl
    engine: str = "zap"
    options: Optional[Dict[str, Any]] = None
    template_id: Optional[int] = None

class TemplateCreate(BaseModel):
    name: str
    engine: str
    description: str = ""
    options: Dict[str, Any] = {}

class ScheduledScanCreate(BaseModel):
    name: str
    target_url: HttpUrl
    engine: str
    frequency: str = "once"
    next_run: datetime
    template_id: Optional[int] = None

class BulkScanCreate(BaseModel):
    urls: List[HttpUrl]
    engine: str = "zap"
    template_id: Optional[int] = None

# API key validation
async def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if x_api_key != settings.VAPT_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return x_api_key

# Favicon endpoint
@app.get("/favicon.ico")
async def favicon():
    """Serve favicon to prevent 404 errors"""
    # Return a simple text response instead of trying to read a non-existent .ico file
    return HTMLResponse(content="""
    <html>
        <head><title>Favicon</title></head>
        <body></body>
    </html>
    """, media_type="text/html")

# Root endpoint - serve the main UI
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main VAPT Scanner dashboard"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>VAPT Scanner</title></head>
            <body>
                <h1>VAPT Scanner API</h1>
                <p>API is running. Access the dashboard at <a href="/static/index.html">/static/index.html</a></p>
                <p>API documentation at <a href="/docs">/docs</a></p>
            </body>
        </html>
        """)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "environment": "development" if settings.DEBUG else "production"
    }

# Core scan endpoints
@app.post("/api/scans/create/", response_model=Dict[str, Any])
async def create_scan(scan_data: ScanCreate, api_key: str = Depends(verify_api_key)):
    """Create a new scan"""
    try:
        template = None
        if scan_data.template_id:
            template = ScanTemplate.objects.get(id=scan_data.template_id)
        
        scan = Scan.objects.create(
            target_url=str(scan_data.target_url),
            engine=scan_data.engine,
            options=scan_data.options or {},
            template=template
        )
        
        # Start scan in background
        run_vapt_scan.delay(scan.id)
        
        return {
            "success": True,
            "id": scan.id,
            "status": scan.status,
            "message": "Scan created and started",
            "target_url": str(scan_data.target_url),
            "engine": scan_data.engine,
            "created_at": scan.start_time.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating scan: {str(e)}")

@app.get("/api/scans/", response_model=List[Dict[str, Any]])
async def list_scans(api_key: str = Depends(verify_api_key)):
    """List all scans"""
    try:
        scans = Scan.objects.all().order_by('-start_time')[:100]
        return [{
            "id": s.id,
            "target_url": s.target_url,
            "engine": s.engine,
            "status": s.status,
            "start_time": s.start_time.isoformat(),
            "end_time": s.end_time.isoformat() if s.end_time else None,
            "findings_count": s.findings_count,
            "critical_findings_count": s.critical_findings_count,
            "error_message": s.error_message
        } for s in scans]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing scans: {str(e)}")

@app.get("/api/scans/{scan_id}/", response_model=Dict[str, Any])
async def get_scan(scan_id: int, api_key: str = Depends(verify_api_key)):
    """Get scan details and results"""
    try:
        scan = Scan.objects.get(id=scan_id)
        return {
            "success": True,
            "id": scan.id,
            "target_url": scan.target_url,
            "engine": scan.engine,
            "status": scan.status,
            "start_time": scan.start_time.isoformat(),
            "end_time": scan.end_time.isoformat() if scan.end_time else None,
            "report_json": scan.report_json,
            "error_message": scan.error_message,
            "findings_count": scan.findings_count,
            "critical_findings_count": scan.critical_findings_count,
            "options": scan.options,
            "template": {
                "id": scan.template.id,
                "name": scan.template.name
            } if scan.template else None
        }
    except Scan.DoesNotExist:
        raise HTTPException(status_code=404, detail="Scan not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting scan: {str(e)}")

@app.get("/api/scans/{scan_id}/logs/", response_model=List[Dict[str, Any]])
async def get_scan_logs(scan_id: int, api_key: str = Depends(verify_api_key)):
    """Get scan logs"""
    try:
        scan = Scan.objects.get(id=scan_id)
        logs = scan.logs.order_by('timestamp')
        return [{
            "timestamp": log.timestamp.isoformat(),
            "level": log.level,
            "message": log.message,
            "context": log.context
        } for log in logs]
    except Scan.DoesNotExist:
        raise HTTPException(status_code=404, detail="Scan not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting logs: {str(e)}")

# Template endpoints
@app.post("/api/templates/create/", response_model=Dict[str, Any])
async def create_template(template_data: TemplateCreate, api_key: str = Depends(verify_api_key)):
    """Create a scan template"""
    try:
        template = ScanTemplate.objects.create(
            name=template_data.name,
            engine=template_data.engine,
            description=template_data.description,
            options=template_data.options
        )
        return {
            "success": True,
            "id": template.id,
            "name": template.name,
            "engine": template.engine,
            "description": template.description,
            "options": template.options,
            "created_at": template.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")

@app.get("/api/templates/", response_model=List[Dict[str, Any]])
async def list_templates(api_key: str = Depends(verify_api_key)):
    """List all templates"""
    try:
        templates = ScanTemplate.objects.filter(is_active=True)
        return [{
            "id": t.id,
            "name": t.name,
            "engine": t.engine,
            "description": t.description,
            "options": t.options,
            "created_at": t.created_at.isoformat(),
            "is_active": t.is_active
        } for t in templates]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing templates: {str(e)}")

# Scheduled scan endpoints
@app.post("/api/scheduled/create/", response_model=Dict[str, Any])
async def create_scheduled_scan(scheduled_data: ScheduledScanCreate, api_key: str = Depends(verify_api_key)):
    """Create a scheduled scan"""
    try:
        template = None
        if scheduled_data.template_id:
            template = ScanTemplate.objects.get(id=scheduled_data.template_id)
        
        scheduled = ScheduledScan.objects.create(
            name=scheduled_data.name,
            target_url=str(scheduled_data.target_url),
            engine=scheduled_data.engine,
            frequency=scheduled_data.frequency,
            next_run=scheduled_data.next_run,
            template=template
        )
        
        return {
            "success": True,
            "id": scheduled.id,
            "name": scheduled.name,
            "target_url": str(scheduled_data.target_url),
            "engine": scheduled_data.engine,
            "frequency": scheduled_data.frequency,
            "next_run": scheduled.next_run.isoformat(),
            "created_at": scheduled.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating scheduled scan: {str(e)}")

@app.get("/api/scheduled/", response_model=List[Dict[str, Any]])
async def list_scheduled_scans(api_key: str = Depends(verify_api_key)):
    """List all scheduled scans"""
    try:
        scheduled = ScheduledScan.objects.filter(is_active=True)
        return [{
            "id": s.id,
            "name": s.name,
            "target_url": s.target_url,
            "engine": s.engine,
            "frequency": s.frequency,
            "next_run": s.next_run.isoformat(),
            "is_active": s.is_active,
            "created_at": s.created_at.isoformat()
        } for s in scheduled]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing scheduled scans: {str(e)}")

# Bulk scan endpoint
@app.post("/api/bulk-scan/", response_model=Dict[str, Any])
async def bulk_scan(bulk_data: BulkScanCreate, api_key: str = Depends(verify_api_key)):
    """Create multiple scans at once"""
    try:
        template = None
        if bulk_data.template_id:
            template = ScanTemplate.objects.get(id=bulk_data.template_id)
        
        scan_ids = []
        for url in bulk_data.urls:
            scan = Scan.objects.create(
                target_url=str(url),
                engine=bulk_data.engine,
                template=template
            )
            run_vapt_scan.delay(scan.id)
            scan_ids.append(scan.id)
        
        return {
            "success": True,
            "message": f"Created {len(scan_ids)} scans",
            "scan_ids": scan_ids,
            "total_urls": len(bulk_data.urls),
            "engine": bulk_data.engine,
            "template_id": bulk_data.template_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating bulk scans: {str(e)}")

# Statistics endpoint
@app.get("/api/stats/", response_model=Dict[str, Any])
async def get_stats(days: int = 30, api_key: str = Depends(verify_api_key)):
    """Get scan statistics"""
    try:
        since = datetime.now() - timedelta(days=days)
        scans = Scan.objects.filter(start_time__gte=since)
        
        from django.db.models import Count, Avg
        
        stats = {
            "success": True,
            "period_days": days,
            "total_scans": scans.count(),
            "completed_scans": scans.filter(status='COMPLETED').count(),
            "failed_scans": scans.filter(status='FAILED').count(),
            "in_progress_scans": scans.filter(status='IN_PROGRESS').count(),
            "pending_scans": scans.filter(status='PENDING').count(),
            "total_findings": Finding.objects.filter(scan__in=scans).count(),
            "critical_findings": Finding.objects.filter(
                scan__in=scans, 
                severity__in=['Critical', 'High']
            ).count(),
            "engine_breakdown": list(scans.values('engine').annotate(count=Count('id'))),
            "status_breakdown": list(scans.values('status').annotate(count=Count('id')))
        }
        
        # Calculate average duration for completed scans
        completed_scans = scans.filter(status='COMPLETED', end_time__isnull=False)
        if completed_scans.exists():
            total_duration = sum([
                (s.end_time - s.start_time).total_seconds() 
                for s in completed_scans
            ], 0)
            stats["avg_duration_seconds"] = total_duration / completed_scans.count()
        else:
            stats["avg_duration_seconds"] = 0
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

# Export endpoint
@app.get("/api/scans/{scan_id}/export/")
async def export_scan(scan_id: int, format: str = "json", api_key: str = Depends(verify_api_key)):
    """Export scan results"""
    try:
        scan = Scan.objects.get(id=scan_id)
        
        if format == "csv":
            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Finding', 'Severity', 'URL', 'Description', 'CVE ID', 'CVSS Score'])
            
            for finding in scan.findings.all():
                writer.writerow([
                    finding.name,
                    finding.severity,
                    finding.url,
                    finding.description,
                    finding.cve_id or '',
                    finding.cvss_score or ''
                ])
            
            output.seek(0)
            return FileResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type='text/csv',
                filename=f'scan_{scan_id}.csv'
            )
        
        elif format == "json":
            data = {
                "success": True,
                "scan": {
                    "id": scan.id,
                    "target_url": scan.target_url,
                    "engine": scan.engine,
                    "status": scan.status,
                    "start_time": scan.start_time.isoformat(),
                    "end_time": scan.end_time.isoformat() if scan.end_time else None,
                },
                "findings": [{
                    "name": f.name,
                    "severity": f.severity,
                    "url": f.url,
                    "description": f.description,
                    "cve_id": f.cve_id,
                    "cvss_score": float(f.cvss_score) if f.cvss_score else None,
                } for f in scan.findings.all()],
                "logs": [{
                    "timestamp": l.timestamp.isoformat(),
                    "level": l.level,
                    "message": l.message,
                    "context": l.context
                } for l in scan.logs.all()]
            }
            return JSONResponse(content=data)
        
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use csv or json")
            
    except Scan.DoesNotExist:
        raise HTTPException(status_code=404, detail="Scan not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting scan: {str(e)}")

# Search endpoint
@app.get("/api/search/", response_model=List[Dict[str, Any]])
async def search_scans(
    q: Optional[str] = None,
    engine: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Search scans with filters"""
    try:
        from django.db.models import Q
        
        scans = Scan.objects.all()
        
        if q:
            scans = scans.filter(
                Q(target_url__icontains=q) |
                Q(notes__icontains=q) |
                Q(findings__name__icontains=q)
            ).distinct()
        
        if engine:
            scans = scans.filter(engine=engine)
        
        if status:
            scans = scans.filter(status=status)
        
        if severity:
            scans = scans.filter(findings__severity=severity).distinct()
        
        return [{
            "id": s.id,
            "target_url": s.target_url,
            "engine": s.engine,
            "status": s.status,
            "start_time": s.start_time.isoformat(),
            "findings_count": s.findings_count,
            "critical_findings_count": s.critical_findings_count
        } for s in scans[:100]]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching scans: {str(e)}")

# Test endpoint
@app.get("/api/test/")
async def test_api(api_key: str = Depends(verify_api_key)):
    """Test API key authentication"""
    return {
        "success": True,
        "message": "API key is valid", 
        "timestamp": datetime.now().isoformat(),
        "api_version": "2.0.0",
        "environment": "development" if settings.DEBUG else "production"
    }

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=settings.API_HOST, 
        port=settings.API_PORT,
        log_level="debug" if settings.DEBUG else "info"
    )
