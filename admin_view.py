from starlette_admin.contrib.sqla.view import ModelView
from starlette_admin.exceptions import FormValidationError
from starlette_admin import RequestAction
from validators import ValidatorsMixin


class MyModelView(ValidatorsMixin, ModelView):
    async def validate(self, request, data):
        if request.state.action == RequestAction.CREATE:
            errors = self.run_create_validators(request, data, None)
            if len(errors) > 0:
                raise FormValidationError(errors)
    
    # async def before_create(self, request, data, obj):
    #     errors = self.run_create_validators(request, data, obj)
    #     if len(errors) > 0:
    #         raise FormValidationError(errors)
    #     return await super().before_create(request, data, obj)
    
    async def before_edit(self, request, data, obj):
        errors = self.run_edit_validators(request, data, obj)
        if len(errors) > 0:
            raise FormValidationError(errors)
