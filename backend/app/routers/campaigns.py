from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.campaign import Campaign
from app.models.communication import CommunicationLog
from app.models.segment import Segment
from app.schemas.campaign import AIMessageResponse, CampaignCreate, CampaignDetail, CampaignOut, CampaignStats
from app.services.ai_service import write_campaign_message
from app.services.segmentation import get_segment_customers
from app.services.sender import personalize
from app.tasks.celery_app import send_campaign_task

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


async def _get_campaign_stats(db: AsyncSession, campaign_id: int) -> CampaignStats:
    result = await db.execute(
        select(CommunicationLog.status, func.count(CommunicationLog.id))
        .where(CommunicationLog.campaign_id == campaign_id)
        .group_by(CommunicationLog.status)
    )
    counts = {row[0]: row[1] for row in result.all()}

    sent = counts.get("sent", 0) + counts.get("delivered", 0) + counts.get("opened", 0) + counts.get("read", 0) + counts.get("clicked", 0)
    delivered = counts.get("delivered", 0) + counts.get("opened", 0) + counts.get("read", 0) + counts.get("clicked", 0)
    failed = counts.get("failed", 0)
    opened = counts.get("opened", 0) + counts.get("read", 0) + counts.get("clicked", 0)
    read = counts.get("read", 0)
    clicked = counts.get("clicked", 0)

    open_rate = (opened / delivered * 100) if delivered > 0 else 0.0
    click_rate = (clicked / delivered * 100) if delivered > 0 else 0.0

    return CampaignStats(
        sent=sent,
        delivered=delivered,
        failed=failed,
        opened=opened,
        read=read,
        clicked=clicked,
        open_rate=round(open_rate, 1),
        click_rate=round(click_rate, 1),
    )


async def _to_campaign_out(db: AsyncSession, campaign: Campaign, include_stats: bool = True) -> CampaignOut:
    segment_result = await db.execute(select(Segment).where(Segment.id == campaign.segment_id))
    segment = segment_result.scalar_one_or_none()
    stats = await _get_campaign_stats(db, campaign.id) if include_stats else None
    return CampaignOut(
        id=campaign.id,
        name=campaign.name,
        segment_id=campaign.segment_id,
        segment_name=segment.name if segment else None,
        channel=campaign.channel,
        message_template=campaign.message_template,
        status=campaign.status,
        created_at=campaign.created_at,
        launched_at=campaign.launched_at,
        stats=stats,
    )


@router.get("", response_model=list[CampaignOut])
async def list_campaigns(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).order_by(Campaign.created_at.desc()))
    campaigns = result.scalars().all()
    return [await _to_campaign_out(db, c) for c in campaigns]


@router.post("", response_model=CampaignOut, status_code=201)
async def create_campaign(data: CampaignCreate, db: AsyncSession = Depends(get_db)):
    segment_result = await db.execute(select(Segment).where(Segment.id == data.segment_id))
    if not segment_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Segment not found")

    campaign = Campaign(**data.model_dump(), status="draft")
    db.add(campaign)
    await db.flush()
    await db.refresh(campaign)
    return await _to_campaign_out(db, campaign)


@router.get("/{campaign_id}", response_model=CampaignDetail)
async def get_campaign(campaign_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return await _to_campaign_out(db, campaign)


@router.post("/{campaign_id}/launch", status_code=202)
async def launch_campaign(campaign_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.status != "draft":
        raise HTTPException(status_code=400, detail=f"Cannot launch campaign in status: {campaign.status}")

    segment_result = await db.execute(select(Segment).where(Segment.id == campaign.segment_id))
    segment = segment_result.scalar_one_or_none()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")

    customers = await get_segment_customers(db, segment.rules)
    if not customers:
        raise HTTPException(status_code=400, detail="Segment has no customers")

    campaign.status = "sending"
    campaign.launched_at = datetime.utcnow()

    for customer in customers:
        recipient_phone = customer.phone
        recipient_email = customer.email
        message = personalize(campaign.message_template, customer.name)
        log = CommunicationLog(
            campaign_id=campaign.id,
            customer_id=customer.id,
            phone=recipient_phone,
            email=recipient_email,
            message=message,
            status="queued",
        )
        db.add(log)

    await db.flush()
    send_campaign_task.delay(campaign_id)

    return {"message": "Campaign launch initiated", "campaign_id": campaign_id, "recipients": len(customers)}


@router.post("/{campaign_id}/ai-message", response_model=AIMessageResponse)
async def ai_message(campaign_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    segment_result = await db.execute(select(Segment).where(Segment.id == campaign.segment_id))
    segment = segment_result.scalar_one_or_none()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")

    segment_dict = {
        "name": segment.name,
        "description": segment.description or "",
    }
    message = await write_campaign_message(segment_dict, "BrewCo", campaign.channel)
    return AIMessageResponse(message=message)
