"""
server.py

Main FastAPI backend for Mobile Chat App.

Features:
- User registration
- Login
- Private messaging
- File uploads
- Message history
- WebSocket communication
- WebRTC audio/video calls
- Group audio/video calls
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
import shutil
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






# ==================================
# CREATE APPLICATION
# ==================================

app = FastAPI(
    title="Mobile Chat App API"
)







# ==================================
# STATIC + TEMPLATES
# ==================================

templates = Jinja2Templates(
    directory="templates"
)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)







# ==================================
# CORS
# ==================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)







# ==================================
# DATABASE
# ==================================

initialize_database()







# ==================================
# HOME PAGE
# ==================================

@app.get("/")
async def home(request: Request):


    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={}

    )







# ==================================
# FILE UPLOAD
# ==================================

@app.post("/upload")
async def upload_file(

    file: UploadFile = File(...)

):


    folder = "uploads"


    os.makedirs(

        folder,

        exist_ok=True

    )


    filepath = os.path.join(

        folder,

        file.filename

    )



    with open(filepath, "wb") as buffer:


        shutil.copyfileobj(

            file.file,

            buffer

        )



    save_attachment(

        None,

        file.filename,

        filepath,

        file.content_type

    )



    return {

        "filename":file.filename,

        "path":filepath,

        "type":file.content_type

    }







# ==================================
# REGISTER
# ==================================

@app.post("/register")
def register(

    user:RegisterRequest

):


    return register_user(

        user.username.strip(),

        user.phone.strip(),

        user.password

    )







# ==================================
# LOGIN
# ==================================

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

        "access_token":token,

        "token_type":"bearer",

        "username":account["username"]

    }







# ==================================
# ONLINE USERS
# ==================================

@app.get("/online")
def online():


    return {

        "users":

        manager.online_users()

    }







# ==================================
# MESSAGE HISTORY
# ==================================

@app.get("/messages/{user1}/{user2}")
def messages(

    user1:str,

    user2:str

):


    first = get_user_by_username(

        user1.strip()

    )


    second = get_user_by_username(

        user2.strip()

    )



    if not first or not second:


        return {

            "messages":[]

        }



    history = get_user_messages(

        first["id"],

        second["id"]

    )


    result=[]



    for msg in history:


        result.append({

            "sender":msg["username"],

            "message":msg["message"],

            "timestamp":msg["timestamp"]

        })



    return {

        "messages":result

    }








# ==================================
# WEBSOCKET SERVER
# ==================================

@app.websocket("/ws/{username}")
async def websocket_endpoint(

    websocket:WebSocket,

    username:str

):


    username=username.strip()



    await manager.connect(

        username,

        websocket

    )



    try:


        while True:


            raw = await websocket.receive_text()


            data=json.loads(raw)


            msg_type=data.get("type")







            # =========================
            # CHAT MESSAGE
            # =========================

            if msg_type=="message":


                receiver=data["receiver"].strip()

                text=data["message"].strip()



                sender=get_user_by_username(

                    username

                )


                receiver_user=get_user_by_username(

                    receiver

                )



                message_id=None



                if sender and receiver_user:


                    chat_id=get_or_create_chat(

                        sender["id"],

                        receiver_user["id"]

                    )


                    message_id=save_message(

                        chat_id,

                        sender["id"],

                        text

                    )



                await manager.send_private_message(

                    receiver,

                    {

                        "type":"message",

                        "sender":username,

                        "message":text,

                        "message_id":message_id

                    }

                )








            # =========================
            # TYPING
            # =========================

            elif msg_type=="typing":


                await manager.send_typing_status(

                    data["receiver"],

                    username,

                    data["typing"]

                )








            # =========================
            # READ RECEIPT
            # =========================

            elif msg_type=="read":


                await manager.send_read_receipt(

                    data["receiver"],

                    data["message_id"]

                )








            # =========================
            # CREATE GROUP CALL
            # =========================

            elif msg_type=="create_call":


                room=data["room"]



                joined = await manager.join_call_room(

                    room,

                    username

                )



                if joined:


                    await websocket.send_text(json.dumps({

                        "type":"call_created",

                        "room":room,

                        "users":

                        manager.get_room_users(room)

                    }))





            # =========================
            # JOIN GROUP CALL
            # =========================

            elif msg_type=="join_call":


                room=data["room"]



                joined = await manager.join_call_room(

                    room,

                    username

                )



                if joined:


                    await manager.broadcast_call_signal(

                        room,

                        username,

                        {

                            "type":"user_joined",

                            "user":username

                        }

                    )



                    await websocket.send_text(json.dumps({

                        "type":"room_users",

                        "users":

                        manager.get_room_users(room)

                    }))







            # =========================
            # WEBRTC GROUP SIGNALS
            # =========================

            elif msg_type in [

                "offer",

                "answer",

                "candidate"

            ]:


                await manager.broadcast_call_signal(

                    data["room"],

                    username,

                    data

                )








            # =========================
            # END CALL
            # =========================

            elif msg_type=="end_call":


                room=data.get("room")



                if room:


                    await manager.broadcast_call_signal(

                        room,

                        username,

                        {

                            "type":"end_call",

                            "user":username

                        }

                    )








            # =========================
            # LEAVE CALL ROOM
            # =========================

            elif msg_type=="leave_call":


                room=data["room"]



                await manager.leave_call_room(

                    room,

                    username

                )



                await manager.broadcast_call_signal(

                    room,

                    username,

                    {

                        "type":"user_left",

                        "user":username

                    }

                )







    except WebSocketDisconnect:


        await manager.disconnect(

            username,

            websocket

        )








# ==================================
# START SERVER
# ==================================

if __name__=="__main__":


    import uvicorn


    uvicorn.run(

        app,

        host="0.0.0.0",

        port=8000

    )
