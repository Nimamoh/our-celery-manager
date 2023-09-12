from sqlalchemy.orm import Session
from our_celery_manager.app.models.ocm.clone import CloneEvent

import logging

logger = logging.getLogger(__name__)

class OcmTaskMetaService():

    def __init__(self, session: Session):
        self.session = session
    
    def record_cloned(self, source_task_id: str, cloned_task_id: str) -> CloneEvent:
        logger.debug(f"Recording cloning of task {source_task_id} with clone one {cloned_task_id}")

        clone_evt = CloneEvent(task_id=source_task_id, clone_id=cloned_task_id)
        self.session.add(clone_evt)
        # raise Exception("ohno")
        self.session.commit()
        self.session.refresh(clone_evt)
        return clone_evt


    @staticmethod
    def make(session: Session):
        return OcmTaskMetaService(session)
