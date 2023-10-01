import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from our_celery_manager.common.settings import settings
from our_celery_manager.models import Base

logger = logging.getLogger(__name__)

engine = create_engine(settings.db_connstring(), logging_name="OCM Engine")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def ocm_metadata():
    return Base.metadata

def init_ddl():
    Base.metadata.create_all(engine)