from pydantic import BaseModel


class Conversation(BaseModel):
    session_id: str
    title: str
    created_at: str
    updated_at: str


class Message(BaseModel):
    role: str
    content: str