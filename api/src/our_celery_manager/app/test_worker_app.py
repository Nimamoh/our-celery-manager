"""Une application celery de test qui peut être utilisé comme worker"""

from celery import Celery
import time

from .settings import settings

celery = Celery(
    "test_app", broker=settings.broker, backend=settings.backend, result_extended=True
)
# celery = Celery('test_app', broker=settings.broker, backend=settings.backend)


@celery.task
def add(x, y):
    return x + y


@celery.task
def child_add(x, y):
    return x + y


@celery.task
def will_fail(msg: str):
    raise Exception(msg)


@celery.task
def ohlong(seconds: int = 5):
    time.sleep(seconds)


@celery.task
def add_n_times(n=5, a=1, b=2):
    for _ in range(n):
        child_add.delay(a, b)
