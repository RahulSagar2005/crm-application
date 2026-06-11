import asyncio
import os

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

from simulator import simulate_delivery

load_dotenv()

app = FastAPI(title="XenoCRM Channel Stub", version="1.0.0")


class SendRequest(BaseModel):
    external_id: str
    recipient: str
    message: str
    channel: str
    callback_url: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/send", status_code=202)
async def send_message(request: SendRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(simulate_delivery, request.external_id, request.callback_url)
    return {
        "message": "Message accepted for delivery",
        "external_id": request.external_id,
        "channel": request.channel,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
