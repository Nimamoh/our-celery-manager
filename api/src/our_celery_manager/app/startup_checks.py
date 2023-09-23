import logging
import sqlparse
from our_celery_manager.app.settings import settings
from our_celery_manager.app.tasks_queue import app as celeryapp

import celery

class SAFormatter(logging.Formatter):
    def format(self, record):
        if 'sqlalchemy.engine' in record.name and record.msg:
            formatted = sqlparse.format(record.msg, reindent = True, keyword_case='upper')
            record.msg = '\n'
            record.msg += formatted

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
    format = '%(levelname)s:%(name)s:%(message)s'
    logging.basicConfig(level=logging.INFO, force=True, format=format)

    if settings.debug:
        logging.info("Debug mode enabled 🐛")

    if settings.debug:
        formatter = SAFormatter(fmt=format)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)

        sa_logger = logging.getLogger("sqlalchemy.engine")
        sa_logger.addHandler(ch)
        sa_logger.setLevel(logging.INFO)
        sa_logger.propagate = False # XXX: important to prevent double logging of sql requests