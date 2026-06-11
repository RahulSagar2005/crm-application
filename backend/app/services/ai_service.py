import json
import re

from groq import Groq

from app.config import get_settings

settings = get_settings()

SEGMENT_SYSTEM_PROMPT = """
You are a CRM segmentation expert. Given a marketer's natural language
query, convert it to structured filter rules for a customer database.

Database has: customers (id, name, email, phone, city, created_at)
and orders (customer_id, amount, product_name, ordered_at, channel).

Return ONLY valid JSON in this exact format:
{
  "segment_name": "short name",
  "description": "what this segment means",
  "rules": {
    "last_order_days_ago": null or number (customers who last ordered X+ days ago),
    "min_total_orders": null or number,
    "max_total_orders": null or number,
    "min_total_spent": null or number,
    "max_total_spent": null or number,
    "city": null or string,
    "channel": null or "online" or "store"
  },
  "reasoning": "brief explanation"
}
Do not include any text outside the JSON.
"""

COPYWRITING_SYSTEM_PROMPT = """
You are a marketing copywriter for D2C brands. Write a personalized
campaign message. Use {name} as the only placeholder. Keep it under
160 chars for SMS, 300 chars for WhatsApp/Email. Be warm, specific,
and include a clear CTA. Return only the message text, nothing else.
"""


def _get_client() -> Groq | None:
    if not settings.groq_api_key:
        return None
    return Groq(api_key=settings.groq_api_key)


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return json.loads(text)


def _fallback_segment(query: str) -> dict:
    query_lower = query.lower()
    rules = {
        "last_order_days_ago": None,
        "min_total_orders": None,
        "max_total_orders": None,
        "min_total_spent": None,
        "max_total_spent": None,
        "city": None,
        "channel": None,
    }
    name = "Custom Segment"
    description = f"Segment based on: {query}"
    reasoning = "Generated using rule-based fallback (no Groq API key configured)."

    if "inactive" in query_lower or "30 day" in query_lower:
        rules["last_order_days_ago"] = 30
        name = "Inactive 30 Days"
        description = "Customers who haven't ordered in the last 30 days"
    elif "high spend" in query_lower or "high value" in query_lower:
        rules["min_total_spent"] = 2000
        name = "High Spenders"
        description = "Customers with total spend over ₹2000"
    elif "mumbai" in query_lower:
        rules["city"] = "Mumbai"
        name = "Mumbai Customers"
        description = "Customers located in Mumbai"

    return {
        "segment_name": name,
        "description": description,
        "rules": rules,
        "reasoning": reasoning,
    }


async def suggest_segment(query: str, db_stats: dict) -> dict:
    client = _get_client()
    if not client:
        return _fallback_segment(query)

    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": SEGMENT_SYSTEM_PROMPT},
            {"role": "user", "content": f"Marketer query: {query}\nDB stats: {db_stats}"},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    return _parse_json_response(response.choices[0].message.content)


def _fallback_message(segment: dict, brand: str, channel: str) -> str:
    first_name_placeholder = "{name}"
    if channel == "sms":
        return f"Hey {first_name_placeholder}! {brand} misses you. Grab 20% off your next brew. Shop now!"
    return (
        f"Hi {first_name_placeholder}! ☕ {brand} has something special for our "
        f"{segment['name']} community. Enjoy exclusive offers on premium coffee. Order today!"
    )


async def write_campaign_message(segment: dict, brand: str, channel: str) -> str:
    client = _get_client()
    if not client:
        return _fallback_message(segment, brand, channel)

    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": COPYWRITING_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Brand: {brand}\nChannel: {channel}\n"
                    f"Segment: {segment['name']}\nDescription: {segment['description']}"
                ),
            },
        ],
        temperature=0.7,
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()
