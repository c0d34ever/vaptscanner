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
            zap.core.access_url(target)
            spider_id = zap.spider.scan(target)
            while int(zap.spider.status(spider_id)) < 100:
                time.sleep(2)
            ascan_id = zap.ascan.scan(target)
            while int(zap.ascan.status(ascan_id)) < 100:
                time.sleep(5)
            alerts = zap.core.alerts(baseurl=target)
            for alert in alerts:
                Finding.objects.create(
                    scan=scan_record,
                    name=alert.get('alert'),
                    severity=alert.get('risk'),
                    description=alert.get('description'),
                    url=alert.get('url') or target,
                )
            scan_record.report_json = alerts

        elif engine == 'nmap':
            args = ['nmap', '-sV', '-O', '-T4', target]
            completed = subprocess.run(args, capture_output=True, text=True)
            scan_record.command_output = completed.stdout + "\n" + completed.stderr
            scan_record.report_json = {'result': 'ok'}

        elif engine == 'sqlmap':
            args = ['sqlmap', '-u', target, '--batch', '--random-agent', '--level=2', '--risk=1', '--crawl=1', '--output-dir=output']
            completed = subprocess.run(args, capture_output=True, text=True)
            scan_record.command_output = completed.stdout + "\n" + completed.stderr
            scan_record.report_json = {'result': 'ok'}

        elif engine == 'wapiti':
            args = ['wapiti', '-u', target, '-f', 'json', '-o', 'wapiti_report.json']
            completed = subprocess.run(args, capture_output=True, text=True)
            scan_record.command_output = completed.stdout + "\n" + completed.stderr
            try:
                with open('wapiti_report.json', 'r', encoding='utf-8') as f:
                    scan_record.report_json = json.load(f)
            except Exception:
                scan_record.report_json = {'result': 'ok'}

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


