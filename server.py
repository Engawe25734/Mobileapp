"""
server.py

Main FastAPI backend for Mobile Chat App.

Features:
- User registration
- User login
- Private messaging
- File uploads
- Message history
- WebSocket chat
- WebRTC audio/video calling
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





# =====================================
# CREATE APP
# =====================================


app = FastAPI(

    title="Mobile Chat App API"

)







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
# DATABASE INIT
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
# =====================================


@app.post("/upload")

async def upload_file(

    file: UploadFile = File(...)

):


    folder = "uploads"


    os.makedirs(

        folder,

        exist_ok=True

    )



    path = os.path.join(

        folder,

        file.filename

    )



    with open(path,"wb") as buffer:


        shutil.copyfileobj(

            file.file,

            buffer

        )




    save_attachment(

        None,

        file.filename,

        path,

        file.content_type

    )



    return {


        "filename":file.filename,


        "path":path,


        "type":file.content_type


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




    token=create_access_token(

        account["id"],

        account["username"]

    )




    return {


        "access_token":token,


        "token_type":"bearer",


        "username":account["username"]

    }









# =====================================
# ONLINE USERS
# =====================================


@app.get("/online")

def online():


    return {


        "users":

        manager.online_users()

    }









# =====================================
# MESSAGE HISTORY
# =====================================


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





    result=[]



    data=get_user_messages(

        first["id"],

        second["id"]

    )




    for msg in data:


        result.append({

            "sender":msg["username"],

            "message":msg["message"],

            "timestamp":msg["timestamp"]

        })




    return {


        "messages":result

    }









# =====================================
# WEBSOCKET
# =====================================


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


            message = await websocket.receive_text()



            data=json.loads(message)



            msg_type=data.get("type")






            # ------------------------------
            # CHAT MESSAGE
            # ------------------------------


            if msg_type=="message":



                receiver=data["receiver"].strip()


                text=data["message"]



                sender_account=get_user_by_username(

                    username

                )



                receiver_account=get_user_by_username(

                    receiver

                )



                message_id=None




                if sender_account and receiver_account:



                    chat_id=get_or_create_chat(

                        sender_account["id"],

                        receiver_account["id"]

                    )



                    message_id=save_message(

                        chat_id,

                        sender_account["id"],

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








            # ------------------------------
            # TYPING
            # ------------------------------


            elif msg_type=="typing":


                await manager.send_typing_status(

                    data["receiver"],

                    username,

                    data["typing"]

                )








            # ------------------------------
            # READ RECEIPT
            # ------------------------------


            elif msg_type=="read":


                await manager.send_read_receipt(

                    data["receiver"],

                    data["message_id"]

                )








            # ------------------------------
            # WEBRTC CALL SIGNALING
            # ------------------------------


            elif msg_type in [


                "call_request",

                "offer",

                "answer",

                "candidate",

                "end_call"


            ]:



                receiver=data["receiver"].strip()



                await manager.send_call_signal(

                    receiver,

                    {


                        **data,


                        "sender":username


                    }

                )





    except WebSocketDisconnect:



        await manager.disconnect(

            username

        )









# =====================================
# RUN SERVER
# =====================================


if __name__=="__main__":


    import uvicorn



    uvicorn.run(

        app,

        host="0.0.0.0",

        port=8000

    )
