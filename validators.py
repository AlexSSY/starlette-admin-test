class ValidatorsMixin:
    create_validators = {}
    edit_validators = {}

    def _run_validators(self, validators, request, data, obj):
        errors = {}

        for field, validator_list in validators.items():
            for v in validator_list:
                error = v(self.model, obj, field, data, request)
                if error:
                    errors[field] = error
                    break

        return errors

    def run_create_validators(self, request, data, obj):
        return self._run_validators(
            self.create_validators,
            request,
            data,
            obj
        )
    
    def run_edit_validators(self, request, data, obj):
        return self._run_validators(
            self.edit_validators,
            request,
            data,
            obj
        )


def min_length_validator(length):

    def validator(model, obj, field, data, request):
        if len(data.get(field)) < length:
            return f"must be greater then {length}"

    return validator


def unique_validator():

    def validator(model, obj, field, data, request):
        model_field = getattr(model, field)
        field_value = data.get(field)
        session = request.state.session
        if session.query(model).where(model_field == field_value).first():
            return "must be unique"
        
    return validator


def unique_edit_validator():

    def validator(model, obj, field, data, request):
        model_field = getattr(model, field)
        field_value = data.get(field)
        session = request.state.session
        with session.no_autoflush:
            if session.query(model).filter(model_field == field_value, model.id != obj.id).first():
                return "already exists"
        
    return validator


def match_validator(other_field):

    def validator(model, obj, field, data, request):
        if data[field] != data[other_field]:
            return f"does not match with '{other_field}' field"

    return validator


def required_validator():

    def validator(model, obj, field, data, request):
        if data.get(field) is None:
            return "required"

    return validator


def check_password_validator(check_password_callback):

    def validator(model, obj, field, data, request):
        plain_password = data.get(field)
        if not check_password_callback(plain_password, obj.password_hash):
            return "wrong password"

    return validator