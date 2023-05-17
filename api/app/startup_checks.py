from app.tasks_queue import app as celeryapp

import celery

def pre_startup_check():
    assert isinstance(celeryapp.backend, celery.backends.database.DatabaseBackend), \
        "Cette application doit obligatoirement être utilisée avec un result backend stocké en base de données"