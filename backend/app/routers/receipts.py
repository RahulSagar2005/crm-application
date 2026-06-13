from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.communication import CommunicationLog
from app.models.customer import Customer
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


@router.get("")
async def list_receipts(
    campaign_id: Optional[int] = Query(None, description="Filter by campaign id"),
    status: Optional[str] = Query(None, description="Filter by status (queued/sent/delivered/opened/clicked/failed)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List delivery receipts, joined with customer name for display.

    Used by the UI to show per-recipient delivery status for a campaign.
    The POST handler above is the inbound callback from the channel-stub.
    """
    stmt = select(CommunicationLog, Customer).join(
        Customer, Customer.id == CommunicationLog.customer_id
    )
    if campaign_id is not None:
        stmt = stmt.where(CommunicationLog.campaign_id == campaign_id)
    if status is not None:
        stmt = stmt.where(CommunicationLog.status == status)
    stmt = stmt.order_by(CommunicationLog.id.desc()).offset(offset).limit(limit)

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "id": log.id,
            "campaign_id": log.campaign_id,
            "customer_id": log.customer_id,
            "customer_name": customer.name,
            "status": log.status,
            "external_id": log.external_id,
            "sent_at": log.sent_at.isoformat() if log.sent_at else None,
            "updated_at": log.updated_at.isoformat() if log.updated_at else None,
        }
        for log, customer in rows
    ]


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
