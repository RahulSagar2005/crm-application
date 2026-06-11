import asyncio
import random
from datetime import datetime

import httpx


async def callback(url: str, external_id: str, status: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            url,
            json={
                "external_id": external_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
            },
            timeout=10,
        )


async def simulate_delivery(external_id: str, callback_url: str):
    await callback(callback_url, external_id, "sent")

    await asyncio.sleep(random.uniform(2, 5))
    if random.random() < 0.08:
        await callback(callback_url, external_id, "failed")
        return
    await callback(callback_url, external_id, "delivered")

    await asyncio.sleep(random.uniform(5, 15))
    if random.random() < 0.60:
        await callback(callback_url, external_id, "opened")

        await asyncio.sleep(random.uniform(3, 8))
        if random.random() < 0.40:
            await callback(callback_url, external_id, "clicked")
