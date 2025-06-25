from contextlib import asynccontextmanager
from html import escape
from starlette.applications import Starlette
from starlette.templating import Jinja2Templates
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqla import Admin
from starlette_admin.fields import PasswordField, TinyMCEEditorField, IntegerField
from dotenv import load_dotenv
from markupsafe import Markup
import os

from models import create_db, User, Post, Comment
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
        IntegerField(name="id", label=Markup('<span class="text-success">ID</span>')),
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
        "posts",
        "comments"
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
    
    async def select2_result(self, obj, request):
        return f'<span><strong>{escape(str(obj.id))}</strong> - {escape(obj.email)}</span>'


class PostModelView(MyModelView):
    exclude_fields_from_create = ["created_at", "updated_at", "comments_count"]
    exclude_fields_from_edit = ["created_at", "updated_at", "comments_count"]
    exclude_fields_from_list = ["comments"]
    fields = [
        "id", 
        "title", 
        TinyMCEEditorField(name="body", label="Body", required=True), 
        "author",
        "comments",
        IntegerField("comments_count"),
        "created_at", 
        "updated_at"
    ]

    create_validators = {
        "title": [validators.unique_validator()],
        "author": [validators.required_validator()]
    }

    edit_validators = {
        "title": [validators.unique_edit_validator()]
    }

    async def repr(self, obj, request):
        return obj.title

    async def select2_result(self, obj, request):
        return f'<span><strong>{escape(str(obj.id))}</strong> - {escape(obj.title)}</span>'


class CommentModelView(MyModelView):
    exclude_fields_from_create = ["created_at", "updated_at"]
    exclude_fields_from_edit = ["created_at", "updated_at"]

    async def repr(self, obj, request):
        return obj.text


admin.add_view(UserModelView(User, "fa-solid fa-users"))
admin.add_view(PostModelView(Post, "fa-brands fa-wordpress"))
admin.add_view(CommentModelView(Comment, "fa-solid fa-comments"))


admin.mount_to(app)
