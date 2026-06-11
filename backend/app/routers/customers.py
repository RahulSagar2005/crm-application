import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.customer import Customer, Order
from app.schemas.customer import CustomerCreate, CustomerDetail, CustomerOut, CustomerUploadResult

router = APIRouter(prefix="/api/customers", tags=["customers"])


async def _enrich_customer(db: AsyncSession, customer: Customer) -> CustomerOut:
    stats = await db.execute(
        select(
            func.count(Order.id),
            func.coalesce(func.sum(Order.amount), 0),
            func.max(Order.ordered_at),
        ).where(Order.customer_id == customer.id)
    )
    total_orders, total_spent, last_order_date = stats.one()
    return CustomerOut(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        city=customer.city,
        created_at=customer.created_at,
        total_orders=total_orders or 0,
        total_spent=float(total_spent or 0),
        last_order_date=last_order_date,
    )


@router.get("", response_model=list[CustomerOut])
async def list_customers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).order_by(Customer.id))
    customers = result.scalars().all()
    return [await _enrich_customer(db, c) for c in customers]


@router.post("", response_model=CustomerOut, status_code=201)
async def create_customer(data: CustomerCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Customer).where(Customer.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already exists")

    customer = Customer(**data.model_dump())
    db.add(customer)
    await db.flush()
    return await _enrich_customer(db, customer)


@router.post("/upload-csv", response_model=CustomerUploadResult)
async def upload_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    created = 0
    skipped = 0
    errors = []

    for i, row in enumerate(reader, start=2):
        try:
            email = row.get("email", "").strip()
            if not email:
                errors.append(f"Row {i}: missing email")
                continue

            existing = await db.execute(select(Customer).where(Customer.email == email))
            if existing.scalar_one_or_none():
                skipped += 1
                continue

            customer = Customer(
                name=row.get("name", "").strip() or "Unknown",
                email=email,
                phone=row.get("phone", "").strip() or None,
                city=row.get("city", "").strip() or None,
            )
            db.add(customer)
            await db.flush()
            created += 1

            amount = row.get("amount")
            product = row.get("product_name")
            if amount and product:
                order = Order(
                    customer_id=customer.id,
                    product_name=product.strip(),
                    amount=float(amount),
                    ordered_at=datetime.utcnow(),
                    channel=row.get("channel", "online").strip() or "online",
                )
                db.add(order)
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    return CustomerUploadResult(created=created, skipped=skipped, errors=errors)


@router.get("/{customer_id}", response_model=CustomerDetail)
async def get_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    base = await _enrich_customer(db, customer)
    orders_result = await db.execute(
        select(Order).where(Order.customer_id == customer_id).order_by(Order.ordered_at.desc())
    )
    orders = orders_result.scalars().all()

    return CustomerDetail(**base.model_dump(), orders=orders)
