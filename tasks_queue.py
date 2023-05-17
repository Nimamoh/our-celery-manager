from celery import Celery

from Settings import Settings

settings = Settings()
app = Celery('tasks', backend=settings.backend)