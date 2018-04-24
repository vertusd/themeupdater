import sys
from datetime import timedelta
sys.path.append('.')

from celery.schedules import crontab
BROKER_URL = 'amqp://celeryuser:celery@66.154.105.251:5672/celeryvhost'
CELERY_RESULT_BACKEND = 'db+mysql://my_db_user:Appuser@01@127.0.0.1/task_result_db'
CELERYD_CONCURRENCY = 1
CELERY_TASK_RESULT_EXPIRES = 18000
CELERY_IMPORTS = ("tasks",)
CELERYBEAT_CHDIR="/home/vertusd/"
CELERYBEAT_SCHEDULE = {
    'makeTasks-every-6-hourss': {
        'task': 'tasks.makeTasks',
        'schedule': crontab(minute="*/15", hour='*'),
        'args': ()
    },
}
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TIMEZONE = 'UTC'
