from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.campaign import Campaign
from app.models.communication import CommunicationLog
from app.routers.campaigns import _get_campaign_stats

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard_analytics(db: AsyncSession = Depends(get_db)):
    from app.models.customer import Customer

    total_customers = await db.scalar(select(func.count(Customer.id)))
    total_campaigns = await db.scalar(select(func.count(Campaign.id)))

    campaigns_result = await db.execute(
        select(Campaign).order_by(Campaign.created_at.desc()).limit(5)
    )
    recent_campaigns = campaigns_result.scalars().all()

    recent = []
    total_open_rate = 0.0
    total_click_rate = 0.0
    launched_count = 0

    for campaign in recent_campaigns:
        stats = await _get_campaign_stats(db, campaign.id)
        if campaign.status in ("sent", "sending"):
            launched_count += 1
            total_open_rate += stats.open_rate
            total_click_rate += stats.click_rate

        from app.models.segment import Segment
        seg_result = await db.execute(select(Segment).where(Segment.id == campaign.segment_id))
        segment = seg_result.scalar_one_or_none()

        recent.append({
            "id": campaign.id,
            "name": campaign.name,
            "segment_name": segment.name if segment else None,
            "status": campaign.status,
            "channel": campaign.channel,
            "sent": stats.sent,
            "open_rate": stats.open_rate,
            "click_rate": stats.click_rate,
            "launched_at": campaign.launched_at.isoformat() if campaign.launched_at else None,
        })

    all_campaigns_result = await db.execute(
        select(Campaign).where(Campaign.status.in_(["sent", "sending"])).order_by(Campaign.launched_at.desc()).limit(7)
    )
    chart_data = []
    for campaign in all_campaigns_result.scalars().all():
        stats = await _get_campaign_stats(db, campaign.id)
        chart_data.append({
            "name": campaign.name[:20],
            "open_rate": stats.open_rate,
            "click_rate": stats.click_rate,
        })

    avg_open = round(total_open_rate / launched_count, 1) if launched_count > 0 else 0.0
    avg_click = round(total_click_rate / launched_count, 1) if launched_count > 0 else 0.0

    return {
        "total_customers": total_customers or 0,
        "total_campaigns": total_campaigns or 0,
        "avg_open_rate": avg_open,
        "avg_click_rate": avg_click,
        "recent_campaigns": recent,
        "chart_data": chart_data,
    }


@router.get("/{campaign_id}")
async def get_campaign_analytics(campaign_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    stats = await _get_campaign_stats(db, campaign_id)

    logs_result = await db.execute(
        select(CommunicationLog)
        .where(CommunicationLog.campaign_id == campaign_id)
        .where(CommunicationLog.updated_at.isnot(None))
        .order_by(CommunicationLog.updated_at)
    )
    logs = logs_result.scalars().all()

    timeline_map: dict[str, dict] = {}
    for log in logs:
        if not log.updated_at:
            continue
        key = log.updated_at.strftime("%Y-%m-%d %H:%M")
        if key not in timeline_map:
            timeline_map[key] = {"time": key, "sent": 0, "delivered": 0, "opened": 0, "clicked": 0, "failed": 0}
        status = log.status
        if status in timeline_map[key]:
            timeline_map[key][status] += 1

    timeline = list(timeline_map.values())

    comms_result = await db.execute(
        select(CommunicationLog)
        .where(CommunicationLog.campaign_id == campaign_id)
        .order_by(CommunicationLog.id)
    )
    communications = []
    for log in comms_result.scalars().all():
        from app.models.customer import Customer
        cust_result = await db.execute(select(Customer).where(Customer.id == log.customer_id))
        customer = cust_result.scalar_one_or_none()
        communications.append({
            "id": log.id,
            "customer_name": customer.name if customer else "Unknown",
            "status": log.status,
            "sent_at": log.sent_at.isoformat() if log.sent_at else None,
            "updated_at": log.updated_at.isoformat() if log.updated_at else None,
        })

    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "status": campaign.status,
        "sent": stats.sent,
        "delivered": stats.delivered,
        "failed": stats.failed,
        "opened": stats.opened,
        "read": stats.read,
        "clicked": stats.clicked,
        "open_rate": stats.open_rate,
        "click_rate": stats.click_rate,
        "timeline": timeline,
        "communications": communications,
    }
