from pathlib import Path
from typing import Annotated
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles

from our_celery_manager.app.models.task.TaskResult import TaskResultPage

from .service.celery.model import SearchField, SortField
from .settings import SettingsApiResponse, settings

from .service.celery.results import result_page, clone_and_send_task
from .startup_checks import pre_startup_check, pre_startup_db_migration

import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(root_path=settings.root_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pre_startup_check()
pre_startup_db_migration()


@app.get("/info", response_model=SettingsApiResponse)
async def info():
    displayable_settings = settings.hiding_passwords()
    return SettingsApiResponse.from_settings(displayable_settings)


@app.get("/results/page", response_model=TaskResultPage)
async def task_result_page(
    request: Request,
    n: int = 0,
    size: int = 10,
    sort: Annotated[list[str], Query()] = [],
    search: Annotated[list[str], Query()] = [],
):
    sorts = [SortField.from_api_str(s) for s in sort if s is not None and s != ""]
    searchs = [SearchField.from_api_str(s) for s in search if s is not None and s != ""]
    results = result_page(size, n, sorts, searchs)
    return results


@app.post("/clone_and_send/{id}")
async def clone_and_send(request: Request, id: str):
    """Clone la tâche et la renvoie sur le broker"""
    r = clone_and_send_task(id)
    return r


static_path = Path(__file__).parent / 'static'
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")