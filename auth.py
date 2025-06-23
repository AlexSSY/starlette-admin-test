from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminUser, AuthProvider, AdminConfig
from starlette_admin.exceptions import LoginFailed

from models import User
from db import SessionLocal
from utils import check_password


auth_exception = LoginFailed('invalid credentials')


class UsernameAndPasswordProvider(AuthProvider):
    async def login(self, username, password, remember_me, request, response):
        with SessionLocal() as session:
            user = session.query(User).filter(User.email == username).first()
        if not user:
            raise auth_exception
        if not check_password(password, user.password_hash):
            raise auth_exception
        request.session.update({'user_id': user.id})
        return response

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
    
    async def is_authenticated(self, request) -> bool:
        user_id = request.session.get("user_id", None)
        if user_id:
            with SessionLocal() as session:
                user = session.query(User).filter(User.id == user_id).first()
            if user:
                request.state.user = user
                return True
        return False
    
    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user  # Retrieve current user
        photo_url = None
        # if user["avatar"] is not None:
        #     photo_url = request.url_for("static", path=user["avatar"])
        return AdminUser(username=user.email, photo_url=photo_url)
    
    def get_admin_config(self, request: Request) -> AdminConfig:
        user = request.state.user  # Retrieve current user
        # Update app title according to current_user
        custom_app_title = "Hello, " + user.email + "!"
        # Update logo url according to current_user
        custom_logo_url = None
        # if user.get("company_logo_url", None):
        #     custom_logo_url = request.url_for("static", path=user["company_logo_url"])
        return AdminConfig(
            app_title=custom_app_title,
            logo_url=custom_logo_url,
        )
