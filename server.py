"""
server.py

Main FastAPI backend for Mobile Chat App.

Features:
- User registration
- Login authentication
- Private messaging
- File uploads
- Message history
- WebSocket communication
- WebRTC audio/video call signaling
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


import shutil
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





# ------------------------------------
# Create application
# ------------------------------------

app = FastAPI(
    title="Mobile Chat App API"
)





# ------------------------------------
# Templates and Static
# ------------------------------------

templates = Jinja2Templates(
    directory="templates"
)



app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)





# ------------------------------------
# CORS
# ------------------------------------

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)





# ------------------------------------
# Database
# ------------------------------------

initialize_database()





# ------------------------------------
# Home page
# ------------------------------------

@app.get("/")
async def home(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={}

    )





# ------------------------------------
# Upload files
# ------------------------------------

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...)
):


    upload_folder = "uploads"


    os.makedirs(
        upload_folder,
        exist_ok=True
    )


    file_path = os.path.join(

        upload_folder,

        file.filename

    )



    with open(
        file_path,
        "wb"
    ) as buffer:


        shutil.copyfileobj(

            file.file,

            buffer

        )



    save_attachment(

        None,

        file.filename,

        file_path,

        file.content_type

    )



    return {

        "filename": file.filename,

        "path": file_path,

        "type": file.content_type

    }





# ------------------------------------
# Register
# ------------------------------------

@app.post("/register")
def register(
    user: RegisterRequest
):


    return register_user(

        user.username.strip(),

        user.phone.strip(),

        user.password

    )





# ------------------------------------
# Login
# ------------------------------------

@app.post("/login")
def login(
    user: LoginRequest
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


        "token_type":"bearer",


        "username":account["username"]


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
# Message History
# ------------------------------------

@app.get("/messages/{user1}/{user2}")
def message_history(

    user1:str,

    user2:str

):


    first_user = get_user_by_username(

        user1.strip()

    )


    second_user = get_user_by_username(

        user2.strip()

    )



    if not first_user or not second_user:


        return {

            "messages":[]

        }



    messages = get_user_messages(

        first_user["id"],

        second_user["id"]

    )



    result=[]



    for msg in messages:


        result.append({

            "sender":msg["username"],

            "message":msg["message"],

            "timestamp":msg["timestamp"]

        })



    return {


        "messages":result


    }





# ------------------------------------
# WebSocket
# ------------------------------------

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



            message_type=data.get("type")





            # --------------------------
            # CHAT MESSAGE
            # --------------------------

            if message_type=="message":


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







            # --------------------------
            # TYPING
            # --------------------------

            elif message_type=="typing":


                await manager.send_typing_status(

                    data["receiver"],

                    username,

                    data["typing"]

                )







            # --------------------------
            # READ RECEIPTS
            # --------------------------

            elif message_type=="read":


                await manager.send_read_receipt(

                    data["receiver"],

                    data["message_id"]

                )







            # --------------------------
            # WEBRTC AUDIO / VIDEO CALL
            # --------------------------

            elif message_type in [

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





# ------------------------------------
# Run
# ------------------------------------

if __name__=="__main__":


    import uvicorn



    uvicorn.run(

        app,

        host="127.0.0.1",

        port=8000

    )
