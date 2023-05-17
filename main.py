from fastapi import FastAPI, Request

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from Settings import Settings
from models import TaskResult

from service.celery.results import get_all_results
from startup_checks import pre_startup_check

settings = Settings()
app = FastAPI()

pre_startup_check()

app.mount('/static', StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

@app.get('/info', response_model=Settings)
async def info():
    return settings

@app.get('/')
async def root(request: Request):
    results = get_all_results()
    ctx = {
        'request': request,
        'results': results,
        'settings': settings.hiding_passwords(),
    }
    return templates.TemplateResponse("index.html", ctx)

@app.get('/results', response_model=list[TaskResult])
async def tasks(request: Request):
    results = get_all_results()
    return results
