"""api/routers/chat.py - Chat and Streaming Route Handlers.

Exposes endpoints for dispatching agent queries, establishing live SSE
event streams, and resolving human-in-the-loop approval decisions.
"""

import asyncio
import json
import uuid
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

from api.core.hitl_manager import hitl_manager
from api.core.session_events import session_event_manager
from api.schemas.chat import ChatRequest
from api.services.nova_services import NovaService
from app.core.event_bus import EventCollector

# Create isolated router instance
router = APIRouter()

# ---------------------------------------------------------------------------
# POST /chat - Dispatch Agent Query in Background
# ---------------------------------------------------------------------------
@router.post("/chat")
async def chat(request: ChatRequest):
    """Receives a user message, sets up an event collection queue,
    and runs the orchestrator asynchronously in the background.
    """
    session_id = request.session_id or str(uuid.uuid4())

    # Create an event queue so the frontend can read real-time events via SSE
    queue = session_event_manager.create_queue(
        session_id=session_id
    )

    # Inject the queue and event loop into the EventCollector
    loop = asyncio.get_running_loop()
    collector = EventCollector(
        queue=queue,
        loop=loop,
    )

    # Initialize the orchestrator service with the session and event handler
    service = NovaService(
        session_id=session_id,
        event_handler=collector,
    )

    # response = await asyncio.to_thread(
    #     service.chat,
    #     request.message,
    # )

    # Run the blocking agent execution in a separate thread so it does not
    # freeze the async FastAPI server, and don't await it here so the endpoint
    # returns immediately with a 200 OK.
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

# ---------------------------------------------------------------------------
# GET /chat/{session_id}/events - Server-Sent Events (SSE) Stream
# ---------------------------------------------------------------------------
@router.get("/chat/{session_id}/events")
async def stream_events(session_id: str):
    """Maintains an open SSE connection yielding status events, intermediate thoughts,
    and final answers as they are emitted by the agent.
    """
    # Fetch the queue created by POST /chat
    queue = session_event_manager.get_queue(session_id=session_id)
    if queue is None:
        return {
            "error": "No active event stream for this session",
        }

    # Async generator that yields SSE data formatted as:
    # event: <event_type>\ndata: <json>\n\n
    try:
        async def event_generator():
            while True:
                # Wait for next event from the agent
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
                # Break and close stream when final answer has been sent
                if event.event_type == "final_answer":
                    break

        return StreamingResponse(
            content=event_generator(),
            media_type="text/event-stream",
        )
    finally:
        # Clean up the queue when the client disconnects or the stream ends
        session_event_manager.remove_queue(session_id=session_id)

# ---------------------------------------------------------------------------
# POST /chat/{session_id}/approval - Human-In-The-Loop (HITL) Decision
# ---------------------------------------------------------------------------
@router.post("/chat/{session_id}/approval")
async def submit_approval(
    session_id: str,
    approved: bool,
):
    """Submits user confirmation or rejection for a blocked tool execution."""
    # Pass user decision to the hitl_manager to unblock the waiting agent thread
    resolved = hitl_manager.submit_decision(
        session_id=session_id,
        approved=approved,
    )
    
    # If no agent was paused waiting for this session ID
    if not resolved:
        return {
            "session_id": session_id,
            "status": "no_pending_approval"
        }

    return {
        "session_id": session_id,
        "status": "approved" if approved else "denied",
    }