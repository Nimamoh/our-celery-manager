from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column
from our_celery_manager.app.models import Base

class CloneEvent(Base):

    __tablename__ = "cloning_events"
    __table_args__ = { "schema": "ocm" }

    id: Mapped[int] = mapped_column(primary_key=True)

    # XXX: it's only event storage, no need to include FK
    # task: Mapped[str] = mapped_column(ForeignKey(TaskExtended.task_id, ondelete="CASCADE"))

    task_id: Mapped[str] = mapped_column(String(36), nullable=False)
    """Task which's been cloned"""
    clone_id: Mapped[str] = mapped_column(String(36), nullable=False)
    """Clone task"""

    created = mapped_column(DateTime(timezone=True), server_default=func.now())
