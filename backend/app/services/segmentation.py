from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer, Order
from app.schemas.customer import CustomerOut


def _customer_stats_subquery():
    return (
        select(
            Order.customer_id,
            func.count(Order.id).label("total_orders"),
            func.coalesce(func.sum(Order.amount), 0).label("total_spent"),
            func.max(Order.ordered_at).label("last_order_date"),
        )
        .group_by(Order.customer_id)
        .subquery()
    )


def build_segment_query(rules: dict):
    stats = _customer_stats_subquery()
    query = (
        select(Customer, stats.c.total_orders, stats.c.total_spent, stats.c.last_order_date)
        .outerjoin(stats, Customer.id == stats.c.customer_id)
    )

    if rules.get("last_order_days_ago") is not None:
        cutoff = datetime.utcnow() - timedelta(days=rules["last_order_days_ago"])
        query = query.where(
            (stats.c.last_order_date < cutoff) | (stats.c.last_order_date.is_(None))
        )

    if rules.get("min_total_orders") is not None:
        query = query.where(func.coalesce(stats.c.total_orders, 0) >= rules["min_total_orders"])

    if rules.get("max_total_orders") is not None:
        query = query.where(func.coalesce(stats.c.total_orders, 0) <= rules["max_total_orders"])

    if rules.get("min_total_spent") is not None:
        query = query.where(func.coalesce(stats.c.total_spent, 0) >= rules["min_total_spent"])

    if rules.get("max_total_spent") is not None:
        query = query.where(func.coalesce(stats.c.total_spent, 0) <= rules["max_total_spent"])

    if rules.get("city"):
        query = query.where(Customer.city.ilike(f"%{rules['city']}%"))

    if rules.get("channel"):
        channel_subq = (
            select(Order.customer_id)
            .where(Order.channel == rules["channel"])
            .distinct()
            .subquery()
        )
        query = query.where(Customer.id.in_(select(channel_subq.c.customer_id)))

    return query


async def get_segment_customers(db: AsyncSession, rules: dict, limit: int | None = None) -> list[CustomerOut]:
    query = build_segment_query(rules)
    if limit:
        query = query.limit(limit)

    result = await db.execute(query)
    customers = []
    for row in result.all():
        customer, total_orders, total_spent, last_order_date = row
        customers.append(
            CustomerOut(
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
        )
    return customers


async def count_segment_customers(db: AsyncSession, rules: dict) -> int:
    stats = _customer_stats_subquery()
    base_query = build_segment_query(rules)
    count_query = select(func.count()).select_from(base_query.subquery())
    result = await db.execute(count_query)
    return result.scalar() or 0


async def get_db_stats(db: AsyncSession) -> dict:
    total_customers = await db.scalar(select(func.count(Customer.id)))
    total_orders = await db.scalar(select(func.count(Order.id)))
    cities = await db.execute(select(Customer.city).distinct().limit(20))
    city_list = [c for c in cities.scalars().all() if c]
    return {
        "total_customers": total_customers or 0,
        "total_orders": total_orders or 0,
        "cities": city_list,
    }
