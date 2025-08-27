from django.core.management.base import BaseCommand
from django.conf import settings
from scans.models import Scan
from scans.tasks import run_vapt_scan


class Command(BaseCommand):
    help = 'Optionally enqueue a scan at startup if STARTUP_SCAN_URL is set'

    def handle(self, *args, **options):
        url = getattr(settings, 'STARTUP_SCAN_URL', None) or None
        engine = getattr(settings, 'STARTUP_SCAN_ENGINE', 'zap')
        if not url:
            self.stdout.write('No STARTUP_SCAN_URL set; skipping initial scan.')
            return
        scan = Scan.objects.create(target_url=url, engine=engine)
        run_vapt_scan.delay(scan.id)
        self.stdout.write(f'Enqueued startup scan {scan.id} for {url} using {engine}.')


