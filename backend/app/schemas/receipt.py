from pydantic import BaseModel


class DeliveryReceipt(BaseModel):
    external_id: str
    status: str
    timestamp: str
