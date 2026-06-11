from datetime import datetime
from pydantic import BaseModel

from app.schemas.customer import CustomerOut


class SegmentRules(BaseModel):
    last_order_days_ago: int | None = None
    min_total_orders: int | None = None
    max_total_orders: int | None = None
    min_total_spent: float | None = None
    max_total_spent: float | None = None
    city: str | None = None
    channel: str | None = None


class SegmentCreate(BaseModel):
    name: str
    description: str | None = None
    rules: dict
    ai_generated: bool = False


class SegmentOut(BaseModel):
    id: int
    name: str
    description: str | None
    rules: dict
    customer_count: int
    created_at: datetime
    ai_generated: bool

    class Config:
        from_attributes = True


class AISegmentRequest(BaseModel):
    query: str


class AISegmentResponse(BaseModel):
    segment_name: str
    description: str
    rules: dict
    reasoning: str
    preview_count: int
    sample_customers: list[CustomerOut]
