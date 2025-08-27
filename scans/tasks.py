import time
from celery import shared_task
from django.utils import timezone
import json
import subprocess
from .models import Scan, Finding
from django.conf import settings
from zapv2 import ZAPv2

zap = ZAPv2(proxies=getattr(settings, 'ZAP_PROXY', {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}))


@shared_task(bind=True)
def run_vapt_scan(self, scan_id: int):
    scan_record = Scan.objects.get(id=scan_id)
    target = scan_record.target_url
    engine = scan_record.engine
    scan_record.status = 'IN_PROGRESS'
    scan_record.task_id = self.request.id
    scan_record.save()
    try:
        if engine == 'zap':
            # Warm up target and spider
            zap.core.access_url(target)
            spider_id = zap.spider.scan(target)
            while int(zap.spider.status(spider_id)) < 100:
                time.sleep(2)
            # Active scan
            ascan_id = zap.ascan.scan(target)
            while int(zap.ascan.status(ascan_id)) < 100:
                time.sleep(5)
            # Wait for passive scan records to drain
            for _ in range(30):
                try:
                    remaining = int(zap.pscan.records_to_scan)
                except Exception:
                    remaining = 0
                if remaining == 0:
                    break
                time.sleep(2)
            # Collect alerts specifically for base URL
            alerts = zap.core.alerts(baseurl=target) or []
            for alert in alerts:
                Finding.objects.create(
                    scan=scan_record,
                    name=(alert.get('alert') or 'ZAP Alert'),
                    severity=(alert.get('risk') or 'Info'),
                    description=(alert.get('description') or ''),
                    url=alert.get('url') or target,
                )
            scan_record.report_json = alerts

        elif engine == 'nmap':
            # Run nmap and parse open ports as findings
            args = ['nmap', '-sV', '-O', '-T4', target]
            completed = subprocess.run(args, capture_output=True, text=True)
            stdout = completed.stdout
            scan_record.command_output = stdout + "\n" + completed.stderr
            open_section = False
            for line in stdout.splitlines():
                if line.strip().lower().startswith('port') and 'state' in line.lower():
                    open_section = True
                    continue
                if open_section and line.strip() == '':
                    open_section = False
                if open_section and '/tcp' in line or '/udp' in line:
                    parts = line.split()
                    if len(parts) >= 3 and parts[1].lower() == 'open':
                        port_proto = parts[0]
                        service = parts[2]
                        Finding.objects.create(
                            scan=scan_record,
                            name=f'Open service: {service}',
                            severity='Info',
                            description=line.strip(),
                            url=target,
                        )
            scan_record.report_json = {'summary': 'nmap completed'}

        elif engine == 'sqlmap':
            args = ['sqlmap', '-u', target, '--batch', '--random-agent', '--level=2', '--risk=1', '--crawl=1']
            completed = subprocess.run(args, capture_output=True, text=True)
            stdout = completed.stdout
            scan_record.command_output = stdout + "\n" + completed.stderr
            # Heuristic parse for discovered injection points
            if 'identified the following injection point' in stdout.lower() or '[critical]' in stdout.lower():
                Finding.objects.create(
                    scan=scan_record,
                    name='SQL injection detected',
                    severity='High',
                    description='sqlmap reported injection vectors. Check command_output for details.',
                    url=target,
                )
            scan_record.report_json = {'summary': 'sqlmap completed'}

        elif engine == 'wapiti':
            args = ['wapiti', '-u', target, '-f', 'json', '-o', 'wapiti_report.json']
            completed = subprocess.run(args, capture_output=True, text=True)
            scan_record.command_output = completed.stdout + "\n" + completed.stderr
            try:
                with open('wapiti_report.json', 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    scan_record.report_json = report
                    vulns = report.get('vulnerabilities') or report.get('vulns') or []
                    for v in vulns:
                        name = v.get('name') or v.get('title') or 'Wapiti finding'
                        level = v.get('level') or v.get('severity') or 'Info'
                        for t in v.get('entries') or v.get('elements') or v.get('targets') or []:
                            url = (t.get('url') or t.get('path') or target)
                            Finding.objects.create(
                                scan=scan_record,
                                name=name,
                                severity=str(level).title(),
                                description=(t.get('method') or '') + ' ' + (t.get('info') or ''),
                                url=url,
                            )
            except Exception:
                scan_record.report_json = {'summary': 'wapiti completed'}

        else:
            raise ValueError(f"Unsupported engine: {engine}")

        scan_record.status = 'COMPLETED'
        scan_record.end_time = timezone.now()
        scan_record.save()
    except Exception as exc:
        scan_record.status = 'FAILED'
        scan_record.error_message = str(exc)
        scan_record.end_time = timezone.now()
        scan_record.save()
        raise


