"""
Data validation models for mobile app.

Used by FastAPI endpoints and WebSocket messages.
"""


from pydantic import BaseModel
from typing import Optional



# ------------------------------------
# User Registration
# ------------------------------------

class RegisterRequest(BaseModel):

    username: str

    phone: str

    password: str



# ------------------------------------
# User Login
# ------------------------------------

class LoginRequest(BaseModel):

    phone: str

    password: str



# ------------------------------------
# JWT Response
# ------------------------------------

class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"



# ------------------------------------
# Private Chat Creation
# ------------------------------------

class ChatRequest(BaseModel):

    receiver_phone: str



# ------------------------------------
# Message Model
# ------------------------------------

class MessageRequest(BaseModel):

    receiver: str

    message: str



# ------------------------------------
# WebSocket Message Format
# ------------------------------------

class WebSocketMessage(BaseModel):

    type: str

    receiver: Optional[str] = None

    message: Optional[str] = None

    message_id: Optional[int] = None



# ------------------------------------
# Typing Indicator
# ------------------------------------

class TypingRequest(BaseModel):

    receiver: str

    typing: bool



# ------------------------------------
# Delivery Receipt
# ------------------------------------

class DeliveryReceipt(BaseModel):

    message_id: int

    receiver: str



# ------------------------------------
# Read Receipt
# ------------------------------------

class ReadReceipt(BaseModel):

    message_id: int

    receiver: str



# ------------------------------------
# Group Creation
# ------------------------------------

class CreateGroupRequest(BaseModel):

    name: str

    members: list[str]



# ------------------------------------
# Add Member To Group
# ------------------------------------

class AddGroupMemberRequest(BaseModel):

    group_id: int

    user_id: int



# ------------------------------------
# Local Sync Request
# ------------------------------------

class SyncRequest(BaseModel):

    last_message_id: int = 0
