from .admin_view import MyModelView
from . import validators


class CommentModelView(MyModelView):
    exclude_fields_from_create = ["created_at", "updated_at"]
    exclude_fields_from_edit = ["created_at", "updated_at"]
    
    create_validators = {
        "post": [validators.required_validator()],
        "author": [validators.required_validator()],
    }

    async def repr(self, obj, request):
        return obj.text
