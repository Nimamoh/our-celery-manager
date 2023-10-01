from celery import Celery

from ..common.settings import settings

celeryapp: Celery = Celery(
    "tasks",
    broker=settings.broker,
    backend=settings.backend,
    result_extended=True,     # Important pour récupérer les proprietés étendues des tâches
)
