"""
server.py

Main FastAPI backend for WhatsApp Clone.
"""


from fastapi import (
FastAPI,
WebSocket,
WebSocketDisconnect,
HTTPException
)

from fastapi.middleware.cors import CORSMiddleware

import json


from database import (
initialize_database,
save_message,
update_user_status,
get_user_by_phone,
get_user_messages,
get_or_create_chat
)


from auth import (
register_user,
authenticate_user,
create_access_token,
verify_token
)


from models import (
RegisterRequest,
LoginRequest
)


from websocket_manager import manager



# ------------------------------------
# Create FastAPI application
# ------------------------------------

app = FastAPI(
title="WhatsApp Clone API"
)



# Allow frontend connections

app.add_middleware(

CORSMiddleware,

allow_origins=["*"],

allow_credentials=True,

allow_methods=["*"],

allow_headers=["*"]

)



# Initialize database

initialize_database()



# Stores connected users

connected_users = {}



# ------------------------------------
# Home route
# ------------------------------------

@app.get("/")
def home():

return {

"message":
"WhatsApp Clone Server Running"

}



# ------------------------------------
# Register endpoint
# ------------------------------------

@app.post("/register")
def register(
user:RegisterRequest
):

result = register_user(

user.username,

user.phone,

user.password

)


return result




# ------------------------------------
# Login endpoint
# ------------------------------------

@app.post("/login")
def login(
user:LoginRequest
):


account = authenticate_user(

user.phone,

user.password

)


if not account:


raise HTTPException(

status_code=401,

detail="Invalid credentials"

)



token = create_access_token(

account["id"],

account["username"]

)


return {

"access_token": token,

"token_type": "bearer",

"username":
account["username"]

}




# ------------------------------------
# Online users
# ------------------------------------

@app.get("/online")
def online_users():

return {

"users":
manager.online_users()

}




# ------------------------------------
# WebSocket Chat
# ------------------------------------

@app.websocket("/ws/{username}")
async def websocket_endpoint(

websocket: WebSocket,

username: str

):


await manager.connect(

username,

websocket

)



try:

while True:


raw = await websocket.receive_text()



data = json.loads(raw)



message_type = data.get(
"type"
)



# -------------------------
# Normal message
# -------------------------

if message_type == "message":


receiver = data["receiver"]

text = data["message"]



sender_account = (
get_user_by_phone(username)
)



if sender_account:


message_id = save_message(

1,

sender_account["id"],

text

)



await manager.send_private_message(

receiver,

{

"type":
"message",

"sender":
username,

"message":
text,

"message_id":
message_id

}

)



# delivery receipt

await manager.send_delivery_receipt(

username,

message_id

)




# -------------------------
# Typing status
# -------------------------

elif message_type == "typing":


await manager.send_typing_status(

data["receiver"],

username,

data["typing"]

)




# -------------------------
# Read receipt
# -------------------------

elif message_type == "read":


await manager.send_read_receipt(

data["receiver"],

data["message_id"]

)



except WebSocketDisconnect:


await manager.disconnect(

username

)
