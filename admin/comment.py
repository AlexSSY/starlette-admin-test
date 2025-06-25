from .admin_view import MyModelView


class CommentModelView(MyModelView):
    exclude_fields_from_create = ["created_at", "updated_at"]
    exclude_fields_from_edit = ["created_at", "updated_at"]

    async def repr(self, obj, request):
        return obj.text
