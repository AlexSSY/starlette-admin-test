from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette_admin.contrib.sqla import Admin, ModelView
from starlette_admin.fields import PasswordField, EmailField
from starlette_admin.exceptions import FormValidationError

from models import create_db, User
from db import engine
import utils


@asynccontextmanager
async def lifespan(app):
    create_db()
    yield


app = Starlette(lifespan=lifespan)
templating = Jinja2Templates('templates')
static_files = StaticFiles(directory='static')
app.mount('/static', static_files, 'static')


def home(request):
    return templating.TemplateResponse(request, 'home.html')

app.add_route('/', home, ['get'], 'home', False)


admin = Admin(engine, title="Example: SQLAlchemy")


class UserModelView(ModelView):
    exclude_fields_from_create = ['created_at', 'updated_at']
    fields = [
        EmailField('email', 'Email', required=True),
        PasswordField('password', 'Password', required=True, exclude_from_list=True, exclude_from_detail=True),
        PasswordField('password_hash', "Hashed password", exclude_from_create=True, exclude_from_edit=True)
    ]

    def validate(self, request, data):
        errors = dict()
        if len(data['password']) < 6:
            errors['password'] = 'too short, minimum 6 symbols'
        if len(errors) > 0:
            raise FormValidationError(errors)
        return super().validate(request, data)

    def before_create(self, request, data, obj):
        plain_password = data.pop('password')
        password_hash = utils.hash_password(plain_password)
        # data['password_hash'] = password_hash
        obj.password_hash = password_hash
        return super().before_create(request, data, obj)


admin.add_view(UserModelView(User))
admin.mount_to(app)
