from pydantic import BaseModel, Field, field_validator, EmailStr, model_validator, ValidationError
from pydantic_core import InitErrorDetails


def validate_match(field1: str, field2: str, loc_on_fail: str = None):
    def decorator(cls: type[BaseModel]):
        original_validate = getattr(cls, "model_validate")

        def new_validate(data):
            model = original_validate(data)
            if getattr(model, field1) != getattr(model, field2):
                raise ValidationError.from_exception_data(
                    "ValidationError",
                    [
                        InitErrorDetails(
                            type="value_error.fields_mismatch",
                            loc=(loc_on_fail or field2,),
                            msg=f"{field1} and {field2} do not match",
                            input=None
                        )
                    ]
                )
            return model

        setattr(cls, "model_validate", classmethod(new_validate))
        return cls

    return decorator


@validate_match('password', 'password_confirmation')
class UserSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    password_confirmation: str


class PostSchema(BaseModel):
    # id: Optional[int] = Field(primary_key=True)
    title: str = Field(min_length=3)
    body: str = Field(min_length=10)
    # views: int = Field(multiple_of=4)
    # user_id: int

    @field_validator("title")
    def title_must_contain_space(cls, v):
        if " " not in v.strip():
            raise ValueError("title must contain a space")
        return v.title()
