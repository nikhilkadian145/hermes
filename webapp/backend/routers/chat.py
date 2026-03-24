from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import sys
import os

# Ensure hermes module is importable
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import hermes.db as db
from ..config import DB_PATH

router = APIRouter(prefix="/api/chat", tags=["chat"])


class SendMessageRequest(BaseModel):
    message: str
    conversation_id: str | None = None  # if None, a new conversation is started


@router.post("/message")
async def send_message(req: SendMessageRequest):
    """
    Accepts a user message from the webapp chat.
    Writes it to chat_messages with status 'pending'.
    Returns immediately — the background thread picks it up asynchronously.
    """
    conversation_id = req.conversation_id or str(uuid.uuid4())
    message_id = db.write_web_chat_user_message(
        DB_PATH, conversation_id, req.message
    )
    return {
        "message_id": message_id,
        "conversation_id": conversation_id,
        "status": "queued"
    }


@router.get("/poll/{conversation_id}")
async def poll_messages(conversation_id: str, after: int = 0):
    """
    Returns new assistant messages since `after` message id.
    Frontend calls this every 1.5 seconds after sending a message.
    Returns empty list if nothing new yet — frontend keeps polling.
    """
    messages = db.get_web_chat_history(DB_PATH, conversation_id, after_id=after)
    assistant_messages = [m for m in messages if m["role"] == "assistant"]
    return {"messages": assistant_messages, "has_new": len(assistant_messages) > 0}


@router.get("/history/{conversation_id}")
async def get_history(conversation_id: str):
    """
    Returns full message history for a conversation (on initial load of a past conversation).
    """
    messages = db.get_web_chat_history(DB_PATH, conversation_id, limit=50)
    return {"messages": messages, "conversation_id": conversation_id}


@router.get("/conversations")
async def list_conversations():
    """
    Returns list of past conversations for the history sidebar.
    """
    conversations = db.get_web_chat_conversations(DB_PATH, limit=20)
    return {"conversations": conversations}
