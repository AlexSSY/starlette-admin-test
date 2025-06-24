from contextlib import asynccontextmanager
from html import escape
from starlette.applications import Starlette
from starlette.templating import Jinja2Templates
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin
from starlette_admin.fields import PasswordField, TinyMCEEditorField, IntegerField
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
    exclude_fields_from_list = ["password_hash", "posts"]
    fields = [
        IntegerField(name="id", label='<span class="text-success">ID</span>'),
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

    edit_validators = {
        "password": [validators.check_password_validator(utils.check_password)],
        "password_confirmation": [validators.match_validator("new_password")]
    }
    
    async def before_edit(self, request, data, obj):
        await super().before_edit(request, data, obj)
        plain_password = data.get("new_password")
        obj.password_hash = utils.hash_password(plain_password)

    async def before_create(self, request, data, obj):
        plain_password = data.get("password")
        obj.password_hash = utils.hash_password(plain_password)
        await super().before_create(request, data, obj)

    async def repr(self, obj, request):
        return obj.email


class PostModelView(MyModelView):
    exclude_fields_from_create = ["created_at", "updated_at"]
    fields = [
        "id", 
        "title", 
        TinyMCEEditorField(name="body", label="Body", required=True), 
        "author",
        "created_at", 
        "updated_at"
    ]

    create_validators = {
        "title": [validators.unique_validator()],
        "author": [validators.required_validator()]
    }

    async def repr(self, obj, request):
        return obj.title

    async def select2_result(self, obj, request):
        result =  f'<span><strong>{escape(str(obj.id))}</strong> - {escape(obj.title)}</span>'
        return result
        # return await super().select2_result(obj, request)


admin.add_view(UserModelView(User, "fa-solid fa-users"))
admin.add_view(PostModelView(Post, "fa-brands fa-wordpress"))


admin.mount_to(app)
