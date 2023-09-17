import logging
import sqlparse
from our_celery_manager.app.settings import settings
from our_celery_manager.app.tasks_queue import app as celeryapp

import celery

class SQLFormatter(logging.Formatter):
    def format(self, record):
        if record.msg:
            formatted = sqlparse.format(record.msg, reindent = True, keyword_case='upper')
            record.msg = formatted

        return super().format(record)

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

def pre_startup_logconf():
    logging.basicConfig(level=logging.INFO, force=True)

    if settings.debug:
        logging.info("Debug mode enabled 🐛")

    if settings.debug:
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(SQLFormatter())
        logging.getLogger("sqlalchemy.engine").addHandler(ch)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)