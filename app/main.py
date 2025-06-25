from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.templating import Jinja2Templates
from dotenv import load_dotenv
import os

from .models import create_db, engine
from admin import core


load_dotenv()
SECRET = os.getenv("SECRET")


@asynccontextmanager
async def lifespan(app):
    create_db()
    yield


app = Starlette(lifespan=lifespan)
templating = Jinja2Templates("templates")
# static_files = StaticFiles(directory='statics')
# app.mount('/statics', static_files, 'statics')


def home(request):
    return templating.TemplateResponse(request, "home.html")


app.add_route("/", home, ["get"], "home", False)


core.setup_admin(engine=engine, app=app, secret_key=SECRET)
