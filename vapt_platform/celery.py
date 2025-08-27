import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vapt_platform.settings')

app = Celery('vapt_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


