from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from sqlalchemy.orm import Session

from fastapi import (
    FastAPI,
    Query,
    Request,
    Depends,
    Response,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from our_celery_manager.app.models.dtos.tasks import ListResult
from our_celery_manager.app import celery_events_subject
from our_celery_manager.app.service.celery.cluster_listener import RelayToWebsocket

from our_celery_manager.app.service.celery.results import (
    clone_and_send_task,
    result_page,
)

from .service.celery.model import SearchField, SortField
from our_celery_manager.common.settings import SettingsApiResponse, settings

from our_celery_manager.db import SessionLocal

import logging

logger = logging.getLogger(__name__)
logger.info("Application up and running 💪")


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    logger.info(f"🧹 cleaning up")
    celery_events_subject.close()
    logger.info(f"🧹 cleaned up")


app = FastAPI(root_path=settings.root_path, lifespan=lifespan)


def get_db():
    """
    Ceates a database session.
    It aims at being used as a fastapi dependency. See: https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-dependency
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/info", response_model=SettingsApiResponse)
async def info():
    displayable_settings = settings.hiding_passwords()
    return SettingsApiResponse.from_settings(displayable_settings)


@app.get("/results/page", response_model=ListResult)
async def task_result_page(
    request: Request,
    n: int = 0,
    size: int = 10,
    sort: Annotated[list[str], Query()] = [],
    search: Annotated[list[str], Query()] = [],
    session: Session = Depends(get_db),
):
    sorts = [SortField.from_api_str(s) for s in sort if s is not None and s != ""]
    searchs = [SearchField.from_api_str(s) for s in search if s is not None and s != ""]
    r = result_page(size, n, sorts, searchs, session)
    return r


@app.post("/clone_and_send/{id}")
async def clone_and_send(request: Request, id: str, session: Session = Depends(get_db)):
    """Clone la tâche et la renvoie sur le broker"""
    r = clone_and_send_task(id, session)
    return r


@app.websocket("/celery-events")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        relay = RelayToWebsocket(websocket)
        celery_events_subject.add_observer(relay)
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect as disconnection:
        logger.debug(f"Socket disconnected", exc_info=disconnection)
        raise
    except Exception as e:
        logger.exception(e, exc_info=e, stack_info=True)
        raise
    finally:
        celery_events_subject.remove_observer(relay)
        await websocket.close()


static_path = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")


@app.exception_handler(Exception)
def handle_exception(req, exception):
    logger.exception(exception, exc_info=exception, stack_info=True)
    return Response("ISE", status_code=500)
