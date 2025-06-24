from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.templating import Jinja2Templates
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin, ModelView
from starlette_admin.fields import PasswordField
from starlette_admin.exceptions import FormValidationError
from starlette_admin import RequestAction
from dotenv import load_dotenv
import os

from models import create_db, User, Post
from db import engine
from auth import UsernameAndPasswordProvider
import utils
from admin_view import MyModelView
import validators


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

base_url = "/admin"
admin = Admin(
    engine,
    title="Admin",
    statics_dir="statics",
    base_url=base_url,
    favicon_url=f"{base_url}/statics/favicon.ico",
    debug=True,
    logo_url=f"{base_url}/statics/logo.svg",
    templates_dir="templates/admin",
    auth_provider=UsernameAndPasswordProvider(),
    middlewares=[Middleware(SessionMiddleware, secret_key=SECRET)],
)


class UserModelView(MyModelView):
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
            'new_password',
            'New Password',
            required=True,
            exclude_from_create=True,
            exclude_from_list=True,
            exclude_from_detail=True
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
        "posts"
    ]

    create_validators = {
        "email": [validators.unique_validator()],
        "password": [validators.min_length_validator(6)],
        "password_confirmation": [validators.match_validator("password")]
    }

    # async def validate(self, request, data):
    #     errors = dict()
    #     parent_validation = await super().validate(request, data)

    #     # * ultra DB-UNIQUE
    #     if request.state.action == RequestAction.CREATE:
    #         session = request.state.session
    #         if (
    #             session.query(self.model)
    #             .where(self.model.email == data["email"])
    #             .first()
    #         ):
    #             errors["email"] = "already exists"

    #         if len(data["password"]) < 6:
    #             errors["password"] = "too short, minimum 6 symbols"

    #         if data["password"] != data["password_confirmation"]:
    #             errors["password_confirmation"] = "password not match"

    #     elif request.state.action == RequestAction.EDIT:
    #         if len(data["new_password"]) < 6:
    #             errors["new_password"] = "too short, minimum 6 symbols"

    #         if data["new_password"] != data["password_confirmation"]:
    #             errors["password_confirmation"] = "password not match"

    #     if len(errors) > 0:
    #         raise FormValidationError(errors)
    #     return parent_validation
    
    def before_edit(self, request, data, obj):
        if not utils.check_password(data.get("password"), obj.password_hash):
            raise FormValidationError({
                'password': 'wrong password'
            })
        plain_password = data.get("new_password")
        obj.password_hash = utils.hash_password(plain_password)
        return super().before_edit(request, data, obj)

    def before_create(self, request, data, obj):
        plain_password = data.get("password")
        obj.password_hash = utils.hash_password(plain_password)
        return super().before_create(request, data, obj)


class PostModelView(ModelView):
    exclude_fields_from_create = ["created_at", "updated_at"]
    fields = [
        "id", 
        "title", 
        "body", 
        # HasOne(name='user_id', label='Author', identity='user', required=True),
        # IntegerField (name="user_id", label='Author ID', required=True),
        "author",
        "created_at", 
        "updated_at"
    ]

    async def  validate(self, request, data):
        errors = {}
        if request.state.action == RequestAction.CREATE:
            session = request.state.session
            if (
                session.query(self.model)
                .where(self.model.title == data["title"])
                .first()
            ):
                errors["title"] = "already exists"

        if data["author"] is None:
            errors["author"] = "author is required"

        if len(errors) > 0:
            raise FormValidationError(errors)
        return await super().validate(request, data)


admin.add_view(UserModelView(User, "fa-solid fa-users"))
admin.add_view(PostModelView(Post, "fa-brands fa-wordpress"))


admin.mount_to(app)
