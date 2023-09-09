import logging
from sqlalchemy import create_engine

from .settings import settings
from .models import Base

logger = logging.getLogger(__name__)

engine = create_engine(settings.db_connstring(), echo=True)

def ocm_metadata():
    return Base.metadata

def init_ddl():
    Base.metadata.create_all(engine)
