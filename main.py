from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette_admin.contrib.sqla import Admin, ModelView
from starlette_admin.fields import PasswordField
from starlette_admin.exceptions import FormValidationError
from starlette_admin import RequestAction
from starlette_admin import statics

from models import create_db, User
from db import engine
import utils


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

base_url = "/admin"
admin = Admin(
    engine,
    title="Admin",
    statics_dir="statics",
    base_url=base_url,
    favicon_url=f"{base_url}/statics/favicon.ico",
    debug=True,
    logo_url=f'{base_url}/statics/logo.svg',
    templates_dir='templates/admin'
)


class UserModelView(ModelView):
    exclude_fields_from_create = ["created_at", "updated_at", "password_hash"]
    exclude_fields_from_edit = ["created_at", "updated_at", "password_hash"]
    exclude_fields_from_list = ["password_hash"]
    fields = [
        "id",
        "email",
        PasswordField(
            "password",
            "Password",
            required=True,
            exclude_from_list=True,
            exclude_from_detail=True,
        ),
        PasswordField(
            "password_confirmation",
            "Password Confirmation",
            required=True,
            exclude_from_list=True,
            exclude_from_detail=True,
        ),
        "password_hash",
        "created_at",
        "updated_at",
    ]

    def validate(self, request, data):
        errors = dict()

        # * ultra DB-UNIQUE
        if request.state.action == RequestAction.CREATE:
            session = request.state.session
            if (
                session.query(self.model)
                .where(self.model.email == data["email"])
                .first()
            ):
                errors["email"] = "already exists"

        if len(data["password"]) < 6:
            errors["password"] = "too short, minimum 6 symbols"
        if data["password"] != data["password_confirmation"]:
            errors["password_confirmation"] = "password not match"
        if len(errors) > 0:
            raise FormValidationError(errors)
        return super().validate(request, data)

    def before_create(self, request, data, obj):
        plain_password = data.get("password")
        obj.password_hash = utils.hash_password(plain_password)
        return super().before_create(request, data, obj)


admin.add_view(UserModelView(User, 'fa-solid fa-users', 'User', 'Users'))
admin.mount_to(app)
