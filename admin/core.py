from starlette_admin.contrib.sqla import Admin
from starlette.middleware import Middleware
from typing import AnyStr, Callable
from starlette.middleware.sessions import SessionMiddleware

# ! tight coupling
from app.models import Post, User, Comment

from .auth import UsernameAndPasswordProvider
from .post import PostModelView
from .user import UserModelView
from .comment import CommentModelView


hash_password: Callable[[AnyStr, AnyStr], AnyStr] = None
check_password = None
def setup_admin(engine, app, secret_key, base_url="/admin"):
    admin = Admin(
        engine,
        title="Admin",
        statics_dir="statics-admin",
        base_url=base_url,
        favicon_url=f"{base_url}/statics/favicon.ico",
        debug=True,
        templates_dir="templates/admin",
        auth_provider=UsernameAndPasswordProvider(),
        middlewares=[Middleware(SessionMiddleware, secret_key=secret_key)],
    )

    admin.add_view(UserModelView(User, "fa-solid fa-users"))
    admin.add_view(PostModelView(Post, "fa-brands fa-wordpress"))
    admin.add_view(CommentModelView(Comment, "fa-solid fa-comments"))
    admin.mount_to(app)
