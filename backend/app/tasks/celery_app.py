import asyncio
from datetime import datetime
from uuid import uuid4

from celery import Celery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.models.campaign import Campaign
from app.models.communication import CommunicationLog
from app.models.customer import Customer
from app.services.sender import personalize, send_to_channel_stub

settings = get_settings()

celery_app = Celery("xenocrm", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

engine = create_async_engine(settings.database_url, echo=False)
sync_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def _send_campaign_async(campaign_id: int):
    async with sync_session_factory() as db:
        campaign_result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
        campaign = campaign_result.scalar_one_or_none()
        if not campaign:
            return

        logs_result = await db.execute(
            select(CommunicationLog)
            .where(CommunicationLog.campaign_id == campaign_id)
            .where(CommunicationLog.status == "queued")
        )
        logs = logs_result.scalars().all()

        for log in logs:
            customer_result = await db.execute(select(Customer).where(Customer.id == log.customer_id))
            customer = customer_result.scalar_one_or_none()
            if not customer:
                continue

            external_id = str(uuid4())
            log.external_id = external_id
            log.status = "sent"
            log.sent_at = datetime.utcnow()
            log.updated_at = datetime.utcnow()

            recipient = customer.phone if campaign.channel in ("whatsapp", "sms") else customer.email
            message = personalize(campaign.message_template, customer.name)

            await send_to_channel_stub(
                external_id=external_id,
                recipient=recipient or "",
                message=message,
                channel=campaign.channel,
            )

        campaign.status = "sent"
        await db.commit()


@celery_app.task(name="send_campaign_task")
def send_campaign_task(campaign_id: int):
    asyncio.run(_send_campaign_async(campaign_id))
