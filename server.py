"""
server.py

Mobile Chat Application Backend

Features:
- User registration
- User login
- Private messaging
- Message history
- File upload
- WebSocket realtime communication
- WebRTC audio/video signaling
- Group call rooms
- API routes
- Media file management
"""


from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    Request,
    UploadFile,
    File
)


from fastapi.templating import Jinja2Templates

from fastapi.staticfiles import StaticFiles

from fastapi.middleware.cors import CORSMiddleware



import os

import json



from database import (

    initialize_database,

    save_message,

    get_user_by_username,

    get_user_messages,

    get_or_create_chat,

    save_attachment

)



from auth import (

    register_user,

    authenticate_user,

    create_access_token

)



from models import (

    RegisterRequest,

    LoginRequest

)



from websocket_manager import manager



# ==============================
# NEW API ROUTES CONNECTION
# ==============================

from api_routes import router



# ==============================
# NEW FILE MANAGER CONNECTION
# ==============================

from file_manager import (

    initialize_storage,

    validate_file,

    save_file

)



# =====================================
# APP CREATION
# =====================================


app = FastAPI(

    title="Mobile Chat Application"

)



# =====================================
# REGISTER API ROUTES
# =====================================


app.include_router(router)



# =====================================
# STATIC FILES
# =====================================


templates = Jinja2Templates(

    directory="templates"

)



app.mount(

    "/static",

    StaticFiles(directory="static"),

    name="static"

)



# =====================================
# UPLOAD FILE STORAGE
# =====================================


UPLOAD_FOLDER = "uploads"



initialize_storage()



app.mount(

    "/uploads",

    StaticFiles(directory=UPLOAD_FOLDER),

    name="uploads"

)
# =====================================
# CORS
# =====================================


app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)



# =====================================
# DATABASE STARTUP
# =====================================


initialize_database()



# =====================================
# HOME PAGE
# =====================================


@app.get("/")
async def home(request: Request):


    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={}

    )



# =====================================
# FILE UPLOAD
# Supports:
# - Images
# - Videos
# - Audio
# - Documents
# =====================================


@app.post("/upload")
async def upload_file(

    file: UploadFile = File(...)

):


    content = await file.read()



    valid, message = validate_file(

        file.filename,

        file.content_type,

        len(content)

    )



    if not valid:


        raise HTTPException(

            status_code=400,

            detail=message

        )



    result = save_file(

        content,

        file.filename

    )



    save_attachment(

        None,

        file.filename,

        result["path"],

        file.content_type

    )



    return {


        "filename": file.filename,


        "url": "/uploads/" + result["stored_name"],


        "type": file.content_type,


        "category":

            file.content_type.split("/")[0]

    }





# =====================================
# REGISTER
# =====================================


@app.post("/register")
def register(

    user:RegisterRequest

):


    return register_user(

        user.username.strip(),

        user.phone.strip(),

        user.password

    )





# =====================================
# LOGIN
# =====================================


@app.post("/login")
def login(

    user:LoginRequest

):


    account = authenticate_user(

        user.phone.strip(),

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


        "username": account["username"]

    }
    # =====================================
# ONLINE USERS
# =====================================


@app.get("/online")
def online():


    return {


        "users": manager.online_users()

    }





# =====================================
# MESSAGE HISTORY
# =====================================


@app.get("/messages/{user1}/{user2}")
def messages(

    user1: str,

    user2: str

):


    first = get_user_by_username(

        user1.strip()

    )


    second = get_user_by_username(

        user2.strip()

    )



    if not first or not second:


        return {


            "messages": []

        }





    records = get_user_messages(

        first["id"],

        second["id"]

    )



    output = []



    for msg in records:


        output.append({


            "sender": msg["username"],


            "message": msg["message"],


            "timestamp": msg["timestamp"]


        })



    return {


        "messages": output

    }





# =====================================
# WEBSOCKET REALTIME CHAT
# =====================================


@app.websocket("/ws/{username}")
async def websocket_endpoint(

    websocket: WebSocket,

    username: str

):


    username = username.strip()



    await manager.connect(

        username,

        websocket

    )



    try:


        while True:


            message = await websocket.receive_text()



            data = json.loads(message)



            msg_type = data.get("type")



            # =========================
            # PRIVATE TEXT MESSAGE
            # =========================


            if msg_type == "message":


                receiver = data["receiver"].strip()


                text = data["message"]




                sender_account = get_user_by_username(

                    username

                )



                receiver_account = get_user_by_username(

                    receiver

                )



                message_id = None



                if sender_account and receiver_account:


                    chat_id = get_or_create_chat(

                        sender_account["id"],

                        receiver_account["id"]

                    )



                    message_id = save_message(

                        chat_id,

                        sender_account["id"],

                        text

                    )



                await manager.send_private_message(

                    receiver,

                    {


                        "type": "message",


                        "sender": username,


                        "message": text,


                        "message_id": message_id


                    }

                )





            # =========================
            # FILE MESSAGE
            # =========================


            elif msg_type == "file":


                receiver = data["receiver"].strip()



                await manager.send_private_message(

                    receiver,

                    {


                        "type": "file",


                        "sender": username,


                        "filename": data["filename"],


                        "url": data["url"],


                        "file_type": data["file_type"]


                    }

                )





            # =========================
            # TYPING INDICATOR
            # =========================


            elif msg_type == "typing":


                await manager.send_typing_status(

                    data["receiver"],

                    username,

                    data["typing"]

                )





            # =========================
            # READ RECEIPT
            # =========================


            elif msg_type == "read":


                await manager.send_read_receipt(

                    data["receiver"],

                    data["message_id"]

                )





            # =========================
            # PRIVATE WEBRTC SIGNALING
            # =========================


            elif msg_type in [

                "offer",

                "answer",

                "candidate"

            ]:


                receiver = data["receiver"]



                await manager.send_private_message(

                    receiver,

                    {


                        **data,


                        "sender": username


                    }

                )
                            # =========================
            # CREATE GROUP CALL ROOM
            # =========================


            elif msg_type == "create_call":


                room = data["room"]



                await manager.join_call_room(

                    room,

                    username

                )



                await websocket.send_text(

                    json.dumps({

                        "type": "call_created",

                        "room": room

                    })

                )





            # =========================
            # JOIN GROUP CALL ROOM
            # =========================


            elif msg_type == "join_call":


                room = data["room"]



                await manager.join_call_room(

                    room,

                    username

                )



                await manager.broadcast_call_signal(

                    room,

                    username,

                    {


                        "type": "user_joined",


                        "user": username


                    }

                )





            # =========================
            # GROUP WEBRTC SIGNALS
            # =========================


            elif msg_type in [


                "group_offer",

                "group_answer",

                "group_candidate"

            ]:


                await manager.broadcast_call_signal(

                    data["room"],

                    username,

                    data

                )





            # =========================
            # END CALL
            # =========================


            elif msg_type == "end_call":


                if "room" in data:


                    await manager.broadcast_call_signal(

                        data["room"],

                        username,

                        data

                    )





            # =========================
            # LEAVE CALL ROOM
            # =========================


            elif msg_type == "leave_call":


                await manager.leave_call_room(

                    data["room"],

                    username

                )



    except WebSocketDisconnect:


        await manager.disconnect(

            username,

            websocket

        )





# =====================================
# SERVER START
# =====================================


if __name__ == "__main__":


    import uvicorn



    uvicorn.run(

        app,

        host="0.0.0.0",

        port=8000

    )
    
