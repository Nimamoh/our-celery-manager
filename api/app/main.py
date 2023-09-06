from typing import Annotated
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles

from app.models.task.TaskResult import TaskResultPage

from .service.celery.model import SearchField, SortField
from .Settings import Settings, SettingsApiResponse

from .service.celery.results import result_page, clone_and_send_task
from .startup_checks import pre_startup_check

import logging

logging.basicConfig(level=logging.INFO)

settings = Settings()  # type: ignore
app = FastAPI(root_path=settings.root_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pre_startup_check()


@app.get("/info", response_model=SettingsApiResponse)
async def info():
    return settings.hiding_passwords()


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


app.mount("/", StaticFiles(directory="app/static", html=True), name="static")