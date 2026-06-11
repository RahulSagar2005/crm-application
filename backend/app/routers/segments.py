from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.segment import Segment
from app.schemas.customer import CustomerOut
from app.schemas.segment import AISegmentRequest, AISegmentResponse, SegmentCreate, SegmentOut
from app.services.ai_service import suggest_segment
from app.services.segmentation import count_segment_customers, get_db_stats, get_segment_customers

router = APIRouter(prefix="/api/segments", tags=["segments"])


@router.get("", response_model=list[SegmentOut])
async def list_segments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Segment).order_by(Segment.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=SegmentOut, status_code=201)
async def create_segment(data: SegmentCreate, db: AsyncSession = Depends(get_db)):
    count = await count_segment_customers(db, data.rules)
    segment = Segment(
        name=data.name,
        description=data.description,
        rules=data.rules,
        customer_count=count,
        ai_generated=data.ai_generated,
    )
    db.add(segment)
    await db.flush()
    await db.refresh(segment)
    return segment


@router.post("/ai-suggest", response_model=AISegmentResponse)
async def ai_suggest_segment(data: AISegmentRequest, db: AsyncSession = Depends(get_db)):
    db_stats = await get_db_stats(db)
    ai_result = await suggest_segment(data.query, db_stats)

    rules = ai_result.get("rules", {})
    preview_count = await count_segment_customers(db, rules)
    sample = await get_segment_customers(db, rules, limit=5)

    return AISegmentResponse(
        segment_name=ai_result.get("segment_name", "AI Segment"),
        description=ai_result.get("description", ""),
        rules=rules,
        reasoning=ai_result.get("reasoning", ""),
        preview_count=preview_count,
        sample_customers=sample,
    )


@router.get("/{segment_id}/customers", response_model=list[CustomerOut])
async def get_segment_customers_list(segment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Segment).where(Segment.id == segment_id))
    segment = result.scalar_one_or_none()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    return await get_segment_customers(db, segment.rules)


@router.delete("/{segment_id}", status_code=204)
async def delete_segment(segment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Segment).where(Segment.id == segment_id))
    segment = result.scalar_one_or_none()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    await db.delete(segment)
