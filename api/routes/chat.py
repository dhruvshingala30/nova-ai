import asyncio
import json
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from api.core.session_events import session_event_manager
from api.schemas.chat import ChatRequest
from api.services.nova_services import NovaService
from app.core.event_bus import EventCollector

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    session_id = request.session_id
    queue = session_event_manager.create_queue(
        session_id=session_id or ""
    )
    
    loop = asyncio.get_running_loop()

    collector = EventCollector(
        queue=queue,
        loop=loop,
    )

    service = NovaService(
        session_id=session_id,
        event_handler=collector,
    )

    # response = await asyncio.to_thread(
    #     service.chat,
    #     request.message,
    # )

    asyncio.create_task(
            asyncio.to_thread(
                service.chat,
                request.message,
            )
        )

    return {
        "session_id": session_id,
        "status": "started",
    }

@router.get("/chat/{session_id}/events")
async def stream_events(session_id: str):
    queue = session_event_manager.get_queue(session_id=session_id)
    if queue is None:
        return {
            "error": "No active event stream for this session",
        }

    async def event_generator():
        while True:
            event = await queue.get()

            payload = {
                    "event_type": event.event_type,
                    "content": event.content,
                    "data": event.data,
                }

            yield (
                f"event: {event.event_type}\n"
                f"data: {json.dumps(payload)}\n\n"
            )

            if event.event_type == "final_answer":
                break

    return StreamingResponse(
        content=event_generator(),
        media_type="text/event-stream",
    )