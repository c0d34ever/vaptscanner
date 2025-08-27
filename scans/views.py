import json
import logging
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import csv
from .models import Scan, Finding, ScanLog, ScanTemplate, ScheduledScan, ScanComparison
from .tasks import run_vapt_scan

logger = logging.getLogger(__name__)


def dashboard(request):
    scans = Scan.objects.all().order_by('-start_time')
    return render(request, 'scans/dashboard.html', {'scans': scans})


def new_scan(request):
    if request.method == 'POST':
        target_url = request.POST.get('target_url')
        engine = request.POST.get('engine') or 'zap'
        if target_url:
            scan = Scan.objects.create(target_url=target_url, engine=engine)
            run_vapt_scan.delay(scan.id)
            return redirect('scan_report', scan_id=scan.id)
    return render(request, 'scans/new_scan.html')


def scan_report(request, scan_id: int):
    scan = get_object_or_404(Scan, id=scan_id)
    findings = scan.findings.all()
    return render(request, 'scans/report.html', {'scan': scan, 'findings': findings})


def _check_api_key(request):
    api_key = request.headers.get('X-API-Key') or request.GET.get('api_key')
    expected = getattr(settings, 'API_KEY', None)
    return api_key and expected and api_key == expected


@csrf_exempt
def api_create_scan(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        return HttpResponseForbidden('Invalid API key')
    data = json.loads(request.body or '{}')
    target_url = data.get('target_url')
    engine = data.get('engine', 'zap')
    options = data.get('options')
    if not target_url:
        return JsonResponse({'error': 'target_url is required'}, status=400)
    scan = Scan.objects.create(target_url=target_url, engine=engine, options=options)
    run_vapt_scan.delay(scan.id)
    return JsonResponse({'id': scan.id, 'status': scan.status})


def api_get_scan(request, scan_id: int):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        return HttpResponseForbidden('Invalid API key')
    scan = get_object_or_404(Scan, id=scan_id)
    return JsonResponse({
        'id': scan.id,
        'target_url': scan.target_url,
        'engine': scan.engine,
        'status': scan.status,
        'start_time': scan.start_time,
        'end_time': scan.end_time,
        'report_json': scan.report_json,
        'error_message': scan.error_message,
    }, safe=False)


def api_list_scans(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        return HttpResponseForbidden('Invalid API key')
    scans = Scan.objects.all().order_by('-start_time')[:100]
    data = [
        {
            'id': s.id,
            'target_url': s.target_url,
            'engine': s.engine,
            'status': s.status,
            'start_time': s.start_time,
            'end_time': s.end_time,
        }
        for s in scans
    ]
    return JsonResponse(data, safe=False)


def api_scan_logs(request, scan_id: int):
    logger.info(f"Logs endpoint called for scan {scan_id}")
    if request.method != 'GET':
        logger.warning(f"Invalid method {request.method} for logs endpoint")
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        logger.warning("Invalid API key for logs endpoint")
        return HttpResponseForbidden('Invalid API key')
    try:
        scan = get_object_or_404(Scan, id=scan_id)
        logger.info(f"Found scan {scan_id}, fetching logs")
        
        # Check if ScanLog model exists (migration might not be applied)
        try:
            from .models import ScanLog
            logs = scan.logs.order_by('timestamp').values('timestamp', 'level', 'message', 'context')
            log_list = list(logs)
            logger.info(f"Returning {len(log_list)} log entries")
            return JsonResponse(log_list, safe=False)
        except Exception as model_error:
            logger.error(f"ScanLog model error: {str(model_error)}")
            return JsonResponse({
                'error': 'ScanLog model not available. Run migrations first.',
                'details': str(model_error)
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error in logs endpoint: {str(e)}")
        return JsonResponse({'error': f'Internal error: {str(e)}'}, status=500)


def api_test(request):
    """Simple test endpoint to verify API key authentication"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        return HttpResponseForbidden('Invalid API key')
    return JsonResponse({'status': 'ok', 'message': 'API key is valid'})


# New API endpoints
@csrf_exempt
def api_create_template(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        return HttpResponseForbidden('Invalid API key')
    
    data = json.loads(request.body or '{}')
    name = data.get('name')
    engine = data.get('engine', 'zap')
    options = data.get('options', {})
    description = data.get('description', '')
    
    if not name:
        return JsonResponse({'error': 'name is required'}, status=400)
    
    template = ScanTemplate.objects.create(
        name=name,
        engine=engine,
        options=options,
        description=description
    )
    return JsonResponse({
        'id': template.id,
        'name': template.name,
        'engine': template.engine
    })


def api_list_templates(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        return HttpResponseForbidden('Invalid API key')
    
    templates = ScanTemplate.objects.filter(is_active=True)
    data = [{
        'id': t.id,
        'name': t.name,
        'engine': t.engine,
        'description': t.description,
        'options': t.options
    } for t in templates]
    return JsonResponse(data, safe=False)


@csrf_exempt
def api_create_scheduled_scan(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        return HttpResponseForbidden('Invalid API key')
    
    data = json.loads(request.body or '{}')
    name = data.get('name')
    target_url = data.get('target_url')
    engine = data.get('engine', 'zap')
    frequency = data.get('frequency', 'once')
    next_run = data.get('next_run')
    template_id = data.get('template_id')
    
    if not all([name, target_url, next_run]):
        return JsonResponse({'error': 'name, target_url, and next_run are required'}, status=400)
    
    template = None
    if template_id:
        template = get_object_or_404(ScanTemplate, id=template_id)
    
    scheduled = ScheduledScan.objects.create(
        name=name,
        target_url=target_url,
        engine=engine,
        frequency=frequency,
        next_run=datetime.fromisoformat(next_run.replace('Z', '+00:00')),
        template=template
    )
    return JsonResponse({
        'id': scheduled.id,
        'name': scheduled.name,
        'next_run': scheduled.next_run.isoformat()
    })


def api_list_scheduled_scans(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        return HttpResponseForbidden('Invalid API key')
    
    scheduled = ScheduledScan.objects.filter(is_active=True)
    data = [{
        'id': s.id,
        'name': s.name,
        'target_url': s.target_url,
        'engine': s.engine,
        'frequency': s.frequency,
        'next_run': s.next_run.isoformat()
    } for s in scheduled]
    return JsonResponse(data, safe=False)


@csrf_exempt
def api_bulk_scan(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        return HttpResponseForbidden('Invalid API key')
    
    data = json.loads(request.body or '{}')
    urls = data.get('urls', [])
    engine = data.get('engine', 'zap')
    template_id = data.get('template_id')
    
    if not urls:
        return JsonResponse({'error': 'urls array is required'}, status=400)
    
    template = None
    if template_id:
        template = get_object_or_404(ScanTemplate, id=template_id)
    
    scan_ids = []
    for url in urls:
        scan = Scan.objects.create(
            target_url=url,
            engine=engine,
            template=template
        )
        run_vapt_scan.delay(scan.id)
        scan_ids.append(scan.id)
    
    return JsonResponse({
        'message': f'Created {len(scan_ids)} scans',
        'scan_ids': scan_ids
    })


def api_scan_stats(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        return HttpResponseForbidden('Invalid API key')
    
    # Get date range from query params
    days = int(request.GET.get('days', 30))
    since = timezone.now() - timedelta(days=days)
    
    scans = Scan.objects.filter(start_time__gte=since)
    
    stats = {
        'total_scans': scans.count(),
        'completed_scans': scans.filter(status='COMPLETED').count(),
        'failed_scans': scans.filter(status='FAILED').count(),
        'in_progress_scans': scans.filter(status='IN_PROGRESS').count(),
        'total_findings': Finding.objects.filter(scan__in=scans).count(),
        'critical_findings': Finding.objects.filter(
            scan__in=scans, 
            severity__in=['Critical', 'High']
        ).count(),
        'engine_breakdown': scans.values('engine').annotate(count=Count('id')),
        'status_breakdown': scans.values('status').annotate(count=Count('id')),
        'avg_duration': scans.filter(
            status='COMPLETED', 
            end_time__isnull=False
        ).aggregate(avg=Avg('end_time' - 'start_time'))
    }
    
    return JsonResponse(stats, safe=False)


def api_export_scan(request, scan_id: int):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        return HttpResponseForbidden('Invalid API key')
    
    scan = get_object_or_404(Scan, id=scan_id)
    format_type = request.GET.get('format', 'json')
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="scan_{scan_id}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Finding', 'Severity', 'URL', 'Description'])
        
        for finding in scan.findings.all():
            writer.writerow([
                finding.name,
                finding.severity,
                finding.url,
                finding.description
            ])
        return response
    
    elif format_type == 'json':
        data = {
            'scan': {
                'id': scan.id,
                'target_url': scan.target_url,
                'engine': scan.engine,
                'status': scan.status,
                'start_time': scan.start_time.isoformat(),
                'end_time': scan.end_time.isoformat() if scan.end_time else None,
                'duration': str(scan.duration) if scan.duration else None,
            },
            'findings': [{
                'name': f.name,
                'severity': f.severity,
                'url': f.url,
                'description': f.description,
                'cve_id': f.cve_id,
                'cvss_score': float(f.cvss_score) if f.cvss_score else None,
            } for f in scan.findings.all()],
            'logs': [{
                'timestamp': l.timestamp.isoformat(),
                'level': l.level,
                'message': l.message,
                'context': l.context
            } for l in scan.logs.all()]
        }
        return JsonResponse(data, safe=False)
    
    return JsonResponse({'error': 'Invalid format. Use csv or json'}, status=400)


def api_search_scans(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        return HttpResponseForbidden('Invalid API key')
    
    query = request.GET.get('q', '')
    engine = request.GET.get('engine', '')
    status = request.GET.get('status', '')
    severity = request.GET.get('severity', '')
    
    scans = Scan.objects.all()
    
    if query:
        scans = scans.filter(
            Q(target_url__icontains=query) |
            Q(notes__icontains=query) |
            Q(findings__name__icontains=query)
        ).distinct()
    
    if engine:
        scans = scans.filter(engine=engine)
    
    if status:
        scans = scans.filter(status=status)
    
    if severity:
        scans = scans.filter(findings__severity=severity).distinct()
    
    data = [{
        'id': s.id,
        'target_url': s.target_url,
        'engine': s.engine,
        'status': s.status,
        'start_time': s.start_time.isoformat(),
        'findings_count': s.findings_count,
        'critical_findings_count': s.critical_findings_count
    } for s in scans[:100]]
    
    return JsonResponse(data, safe=False)


