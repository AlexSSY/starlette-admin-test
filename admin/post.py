from starlette_admin.fields import IntegerField, DateTimeField, TinyMCEEditorField
from html import escape

from .admin_view import MyModelView
from . import validators


class CommentsCountField(IntegerField):
    async def parse_obj(self, request, obj):
        return obj.comments_count


class PostModelView(MyModelView):
    exclude_fields_from_create = ["created_at", "updated_at", "comments_count", "comments"]
    exclude_fields_from_edit = ["created_at", "updated_at", "comments_count", "comments"]
    exclude_fields_from_list = ["comments"]
    fields = [
        "id", 
        "title", 
        TinyMCEEditorField(name="body", label="Body", required=True), 
        "author",
        "comments",
        CommentsCountField("comments_count", render_function_key="post_comments_count"),
        DateTimeField("created_at", output_format="%B %d, %Y %H:%M:%S"), 
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
