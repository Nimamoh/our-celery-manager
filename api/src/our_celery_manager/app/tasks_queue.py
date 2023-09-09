from celery import Celery

from .settings import settings

app: Celery = Celery(
    "tasks",
    broker=settings.broker,
    backend=settings.backend,
    result_extended=True,     # Important pour récupérer les proprietés étendues des tâches
)
