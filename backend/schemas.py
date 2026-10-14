from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class RegisterRequest(BaseModel):
    name: str | None = None
    email: str
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        value = value.strip().lower()
        local, _, domain = value.partition("@")
        if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
            raise ValueError("Enter a valid email address")
        return value

    @field_validator("name")
    @classmethod
    def blank_name_to_none(cls, value: str | None) -> str | None:
        return (value or "").strip() or None


class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None


class OrderStatusUpdate(BaseModel):
    status: str = "completed"
