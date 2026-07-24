"""
server.py

Main FastAPI backend for WhatsApp Clone.
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
    get_user_by_phone,
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
# Create FastAPI application
# ------------------------------------

app = FastAPI(
    title="mobile app API"
)


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
# Initialize database
# ------------------------------------

initialize_database()

# ------------------------------------
# Home route
# ------------------------------------

@app.get("/")
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )



# ------------------------------------
# File upload endpoint
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

    result = register_user(

        user.username,

        user.phone,

        user.password

    )


    return result




# ------------------------------------
# Login
# ------------------------------------

@app.post("/login")
def login(
    user: LoginRequest
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

        "username": account["username"]

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
# Message history
# ------------------------------------

@app.get("/messages/{user1}/{user2}")
def message_history(

    user1: str,

    user2: str

):


    first_user = get_user_by_phone(
        user1
    )


    second_user = get_user_by_phone(
        user2
    )


    if not first_user or not second_user:

        return {

            "messages": []

        }



    messages = get_user_messages(

        first_user["id"],

        second_user["id"]

    )



    result = []


    for msg in messages:

        result.append({

            "sender":
            msg["username"],

            "message":
            msg["message"],

            "timestamp":
            msg["timestamp"]

        })



    return {

        "messages": result

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



                sender_account = get_user_by_phone(

                    username

                )



                if sender_account:


                    receiver_account = get_user_by_phone(

                        receiver

                    )



                    if receiver_account:


                        chat_id = get_or_create_chat(

                            sender_account["id"],

                            receiver_account["id"]

                        )


                        message_id = save_message(

                            chat_id,

                            sender_account["id"],

                            text

                        )


                    else:

                        message_id = None



                else:

                    message_id = None



                await manager.send_private_message(

                    receiver,

                    {

                        "type": "message",

                        "sender": username,

                        "message": text,

                        "message_id": message_id

                    }

                )



                if message_id:


                    await manager.send_delivery_receipt(

                        username,

                        message_id

                    )




            # -------------------------
            # File message
            # -------------------------

            elif message_type == "file":


                await manager.send_private_message(

                    data["receiver"],

                    {

                        "type": "file",

                        "sender": username,

                        "filename": data["filename"],

                        "path": data["path"],

                        "filetype": data["filetype"]

                    }

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



# ------------------------------------
# Run server
# ------------------------------------

if __name__ == "__main__":

    import uvicorn


    uvicorn.run(

        app,

        host="127.0.0.1",

        port=8000

    )
