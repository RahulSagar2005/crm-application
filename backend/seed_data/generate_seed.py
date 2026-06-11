import asyncio
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.models.customer import Customer, Order

settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

fake = Faker("en_IN")

PRODUCTS = [
    "Cold Brew", "Espresso", "Filter Coffee",
    "Cappuccino", "Latte", "Mocha", "Americano",
]

INDIAN_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow",
]


async def generate_seed():
    async with async_session() as db:
        existing = await db.scalar(select(Customer.id).limit(1))
        if existing:
            print("Database already has data. Skipping seed.")
            return

        print("Generating 500 customers with orders...")

        for i in range(1, 501):
            name = fake.name()
            email = fake.unique.email()
            phone = fake.phone_number()[:15]
            city = random.choice(INDIAN_CITIES)

            try:
                customer = Customer(
                    name=name,
                    email=email,
                    phone=phone,
                    city=city,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
                )
                db.add(customer)
                await db.flush()
            except Exception:
                fake.unique.clear()
                continue

            num_orders = random.randint(1, 8)
            is_inactive = i <= 150  # 30% inactive
            is_high_value = 151 <= i <= 250  # 20% high value

            order_dates = []
            for _ in range(num_orders):
                if is_inactive:
                    days_ago = random.randint(31, 90)
                else:
                    days_ago = random.randint(0, 30 if not is_high_value else 60)
                order_dates.append(datetime.utcnow() - timedelta(days=days_ago))

            order_dates.sort()

            for j, ordered_at in enumerate(order_dates):
                if is_high_value and j == num_orders - 1:
                    amount = random.uniform(500, 1500)
                elif is_high_value:
                    amount = random.uniform(200, 800)
                else:
                    amount = random.uniform(150, 600)

                order = Order(
                    customer_id=customer.id,
                    product_name=random.choice(PRODUCTS),
                    amount=round(amount, 2),
                    ordered_at=ordered_at,
                    channel=random.choice(["online", "store"]),
                )
                db.add(order)

            if i % 50 == 0:
                print(f"  Created {i}/500 customers...")
                await db.commit()

        await db.commit()
        print("Seed data generation complete! 500 customers created.")


if __name__ == "__main__":
    asyncio.run(generate_seed())
