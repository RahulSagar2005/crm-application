from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.communication import CommunicationLog
from app.schemas.receipt import DeliveryReceipt

router = APIRouter(prefix="/api/receipts", tags=["receipts"])

STATUS_ORDER = {
    "queued": 0,
    "sent": 1,
    "failed": 1,
    "delivered": 2,
    "opened": 3,
    "read": 4,
    "clicked": 5,
}


@router.post("")
async def receive_receipt(receipt: DeliveryReceipt, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CommunicationLog).where(CommunicationLog.external_id == receipt.external_id)
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Communication log not found")

    if log.status == "failed":
        return {"message": "Ignored — already failed"}

    current_order = STATUS_ORDER.get(log.status, 0)
    new_order = STATUS_ORDER.get(receipt.status, 0)

    if receipt.status == "failed":
        log.status = "failed"
    elif new_order > current_order:
        log.status = receipt.status

    try:
        log.updated_at = datetime.fromisoformat(receipt.timestamp.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        log.updated_at = datetime.utcnow()

    return {"message": "Receipt processed", "status": log.status}
