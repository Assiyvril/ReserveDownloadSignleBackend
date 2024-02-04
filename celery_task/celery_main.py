from __future__ import absolute_import, unicode_literals

import datetime
import time

from celery import Celery
from scripts_public import _setup_django


celery_app = Celery('slp_web_server')
celery_app.config_from_object('celery_task.celery_config', namespace='CELERY')

celery_app.autodiscover_tasks([
    'celery_task.reserve_download.task',
])
