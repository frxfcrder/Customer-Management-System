from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


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
