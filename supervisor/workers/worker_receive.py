from celery import Celery
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

app = Celery('receive_worker')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.task_routes = {
    'receive_sensor_data': {'queue': 'receive_sensor'},
}

app.autodiscover_tasks(['supervisor.tasks'])

if __name__ == '__main__':
    app.start()
