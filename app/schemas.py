from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatGPTRequest(BaseModel):
    model: str
    user_id: str
    question: str

class AnthropicRequest(BaseModel):
    model: str
    user_id: str
    question: str

class Interaction(BaseModel):
    _id: Optional[str] = None
    user_id: str
    datetime: str
    question: str
    answer: str
    model: str

class InteractionResponse(BaseModel):
    message: str
    interaction_id: Optional[str] = None
