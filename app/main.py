from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from dotenv import load_dotenv
import os

from .models import create_db, engine
from admin import core


load_dotenv()
SECRET = os.getenv("SECRET")
CURRENT_DIR = os.path.dirname(__file__)


@asynccontextmanager
async def lifespan(app):
    create_db()
    yield


app = Starlette(lifespan=lifespan)
templating = Jinja2Templates("templates")
static_files = StaticFiles(directory='statics')
app.mount('/static-local', static_files, 'static-local')


def home(request):
    return templating.TemplateResponse(request, "home.html")


app.add_route("/", home, ["get"], "home", False)


core.setup_admin(engine=engine, app=app, secret_key=SECRET)
