from datetime import datetime
from pydantic import BaseModel


class CampaignCreate(BaseModel):
    name: str
    segment_id: int
    channel: str
    message_template: str


class CampaignStats(BaseModel):
    sent: int = 0
    delivered: int = 0
    failed: int = 0
    opened: int = 0
    read: int = 0
    clicked: int = 0
    open_rate: float = 0.0
    click_rate: float = 0.0


class CampaignOut(BaseModel):
    id: int
    name: str
    segment_id: int
    segment_name: str | None = None
    channel: str
    message_template: str
    status: str
    created_at: datetime
    launched_at: datetime | None = None
    stats: CampaignStats | None = None

    class Config:
        from_attributes = True


class CampaignDetail(CampaignOut):
    pass


class AIMessageResponse(BaseModel):
    message: str
