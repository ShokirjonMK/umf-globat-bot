from __future__ import absolute_import, unicode_literals
import os
from celery.schedules import crontab
from celery import Celery
import environ

# Env ni yuklaymiz
env = environ.Env()
env.read_env(os.path.join(os.getcwd(), ".envs/.production/.django"))

# Django settings faylini o‘rnatamiz
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

app = Celery('config')

# Django settings.py ichidan `CELERY_` bilan boshlanuvchi sozlamalarni o‘qiydi
app.config_from_object('django.conf:settings', namespace='CELERY')

# 🔥 To‘g‘ridan-to‘g‘ri .env fayldan broker va backend
app.conf.update(
    broker_url=env('CELERY_BROKER_URL'),
    result_backend=env('CELERY_RESULT_BACKEND'),
)


# app.conf.beat_schedule = {
#     'run_tasks': {
#         'task': 'myapp.tasks.backup_and_send_to_telegram',
#         'schedule': crontab(hour=0, minute=0)
#     },
# }



# Tasklarni avtomatik topadi
app.autodiscover_tasks()
