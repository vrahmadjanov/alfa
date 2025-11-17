"""
Конфигурация Celery для асинхронных задач
"""
import os
from celery import Celery

# Устанавливаем переменную окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alfa.settings')

app = Celery('alfa')

# Загружаем конфигурацию из настроек Django с префиксом CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи во всех приложениях
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Отладочная задача для проверки работы Celery"""
    print(f'Request: {self.request!r}')

