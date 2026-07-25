"""
api_routes.py

chatMe API Routes

Provides:
- Profile management
- Contacts
- Messages
- Attachments
- Reactions
- Notifications
- Calls

Used by:
- server.py
"""


from fastapi import APIRouter, UploadFile, File

import os

import shutil


from database_manager import (

    get_user,

    save_message,

    get_messages,

    add_reaction,

    save_notification,

    save_call

)





router = APIRouter()





# =====================================
# USER PROFILE
# =====================================


@router.get("/profile/{username}")
def profile(

    username:str

):


    user = get_user(

        username

    )


    if not user:


        return {


            "error":"User not found"


        }



    return {


        "id":user[0],

        "username":user[1],

        "phone":user[2],

        "profile_picture":user[4],

        "bio":user[5],

        "status":user[6],

        "last_seen":user[7]

    }







# =====================================
# SEND MESSAGE API
# =====================================


@router.post("/message")
def send_message_api(

    sender:str,

    receiver:str,

    message:str

):


    save_message(

        sender,

        receiver,

        message

    )


    save_notification(

        receiver,

        sender,

        "New Message",

        message,

        "message"

    )


    return {


        "status":"sent"


    }







# =====================================
# MESSAGE HISTORY
# =====================================


@router.get("/messages/{user1}/{user2}")
def message_history(

    user1:str,

    user2:str

):


    messages = get_messages(

        user1,

        user2

    )


    result=[]



    for msg in messages:


        result.append(

        {


            "id":msg[0],

            "sender":msg[1],

            "receiver":msg[2],

            "message":msg[3],

            "attachment":msg[4],

            "status":msg[5],

            "time":msg[7]


        }

        )



    return {


        "messages":result


    }







# =====================================
# FILE UPLOAD
# =====================================


@router.post("/attachment/upload")
async def upload_attachment(

    file:UploadFile=File(...)

):


    folder="uploads"


    os.makedirs(

        folder,

        exist_ok=True

    )



    path=os.path.join(

        folder,

        file.filename

    )



    with open(

        path,

        "wb"

    ) as buffer:


        shutil.copyfileobj(

            file.file,

            buffer

        )



    return {


        "filename":file.filename,

        "path":path,

        "type":file.content_type


    }







# =====================================
# MESSAGE REACTION
# =====================================


@router.post("/reaction")
def reaction(

    message_id:int,

    username:str,

    emoji:str

):


    add_reaction(

        message_id,

        username,

        emoji

    )


    return {


        "status":"reaction added"


    }







# =====================================
# NOTIFICATION
# =====================================


@router.post("/notification")
def notification(

    receiver:str,

    sender:str,

    message:str

):


    save_notification(

        receiver,

        sender,

        "chatMe",

        message,

        "system"

    )


    return {


        "status":"created"


    }







# =====================================
# CALL HISTORY
# =====================================


@router.post("/call")
def call_history(

    caller:str,

    receiver:str,

    call_type:str,

    status:str

):


    save_call(

        caller,

        receiver,

        call_type,

        status

    )


    return {


        "status":"saved"


    }







# =====================================
# HEALTH CHECK
# =====================================


@router.get("/health")
def health():


    return {


        "app":"chatMe",

        "status":"running"


    }
