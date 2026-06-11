import httpx

from app.config import get_settings

settings = get_settings()


def personalize(template: str, customer_name: str) -> str:
    first_name = customer_name.split()[0] if customer_name else "there"
    return template.replace("{name}", first_name)


async def send_to_channel_stub(
    external_id: str,
    recipient: str,
    message: str,
    channel: str,
) -> bool:
    callback_url = f"{settings.crm_base_url}/api/receipts"
    payload = {
        "external_id": external_id,
        "recipient": recipient,
        "message": message,
        "channel": channel,
        "callback_url": callback_url,
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.channel_stub_url}/send",
                json=payload,
                timeout=30.0,
            )
            return response.status_code == 202
    except httpx.HTTPError:
        return False
