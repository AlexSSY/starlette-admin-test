from starlette_admin.fields import IntegerField, PasswordField
from markupsafe import Markup
from html import escape

from .admin_view import MyModelView
from . import validators
from app import utils


class UserModelView(MyModelView):
    exclude_fields_from_create = ["created_at", "updated_at", "password_hash", "comments", "posts"]
    exclude_fields_from_edit = ["created_at", "updated_at", "password_hash", "comments", "posts"]
    exclude_fields_from_list = ["password_hash", "posts", "comments"]
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
