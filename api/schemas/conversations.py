from pydantic import BaseModel


class Conversation(BaseModel):
    session_id: str


class Message(BaseModel):
    role: str
    content: str