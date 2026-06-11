from datetime import datetime
from pydantic import BaseModel, EmailStr


class OrderOut(BaseModel):
    id: int
    product_name: str
    amount: float
    ordered_at: datetime
    channel: str

    class Config:
        from_attributes = True


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    city: str | None = None


class CustomerOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    city: str | None
    created_at: datetime
    total_orders: int = 0
    total_spent: float = 0.0
    last_order_date: datetime | None = None

    class Config:
        from_attributes = True


class CustomerDetail(CustomerOut):
    orders: list[OrderOut] = []


class CustomerUploadResult(BaseModel):
    created: int
    skipped: int
    errors: list[str] = []
