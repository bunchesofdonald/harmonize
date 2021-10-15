import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'harmonize.settings')

app = Celery('harmonize', broker='redis://192.168.0.218:6379/7')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
