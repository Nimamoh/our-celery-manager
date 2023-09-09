from our_celery_manager.app.tasks_queue import app as celeryapp

import celery

def pre_startup_check():
    assert isinstance(celeryapp.backend, celery.backends.database.DatabaseBackend), \
        "Cette application doit obligatoirement être utilisée avec un result backend stocké en base de données"

def pre_startup_db_migration():
    import alembic.config
    args = [
        '--raiseerr',
        'upgrade', 'head'
    ]
    alembic.config.main(argv=args)