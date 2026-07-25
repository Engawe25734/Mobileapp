"""
notifications.py

chatMe Notification Manager

Features:
- Push notification support
- Message alerts
- Call alerts
- Online status notifications
- Firebase Cloud Messaging ready

Used by:
- server.py
- websocket_manager.py
- app.js
"""


import datetime
import uuid



# =====================================
# NOTIFICATION STORAGE
# =====================================


notifications = {}



device_tokens = {}





# =====================================
# REGISTER DEVICE
# =====================================


def register_device(

    username,

    token

):

    """
    Store user device token

    Used for:
    - Android
    - iOS
    - Browser notifications
    """



    device_tokens[username] = token



    return {


        "success":True,


        "username":username,


        "token":token


    }






# =====================================
# REMOVE DEVICE
# =====================================


def remove_device(

    username

):


    if username in device_tokens:


        del device_tokens[username]


        return True



    return False






# =====================================
# CREATE NOTIFICATION
# =====================================


def create_notification(

    receiver,

    sender,

    title,

    message,

    notification_type="message"

):


    """
    Create notification record
    """



    notification_id = str(

        uuid.uuid4()

    )



    data = {


        "id":notification_id,


        "receiver":receiver,


        "sender":sender,


        "title":title,


        "message":message,


        "type":notification_type,


        "time":str(

            datetime.datetime.now()

        ),


        "read":False


    }




    if receiver not in notifications:


        notifications[receiver] = []



    notifications[receiver].append(

        data

    )



    return data





# =====================================
# NEW MESSAGE NOTIFICATION
# =====================================


def message_notification(

    sender,

    receiver,

    message

):


    return create_notification(

        receiver,

        sender,

        "New Message",

        message,

        "message"

    )






# =====================================
# CALL NOTIFICATION
# =====================================


def call_notification(

    caller,

    receiver,

    call_type="video"

):


    return create_notification(

        receiver,

        caller,

        "Incoming Call",

        f"{caller} started a {call_type} call",

        "call"

    )






# =====================================
# ONLINE STATUS NOTIFICATION
# =====================================


def online_notification(

    username,

    friend

):


    return create_notification(

        friend,

        username,

        "Online Status",

        f"{username} is now online",

        "status"

    )






# =====================================
# GET USER NOTIFICATIONS
# =====================================


def get_notifications(

    username

):


    return notifications.get(

        username,

        []

    )






# =====================================
# MARK AS READ
# =====================================


def mark_read(

    username,

    notification_id

):


    user_notifications = notifications.get(

        username,

        []

    )



    for item in user_notifications:


        if item["id"] == notification_id:


            item["read"] = True


            return True



    return False






# =====================================
# FIREBASE PLACEHOLDER
# =====================================


def send_push_notification(

    token,

    title,

    body

):

    """
    Firebase Cloud Messaging integration point.

    Later replace this function with:

    firebase_admin.messaging.send()

    """



    print(

        "Push notification sent"

    )


    print(

        "Token:",

        token

    )


    print(

        "Title:",

        title

    )


    print(

        "Message:",

        body

    )



    return True






# =====================================
# TEST
# =====================================


if __name__ == "__main__":


    register_device(

        "elvis",

        "device_token_123"

    )



    note = message_notification(

        "john",

        "elvis",

        "Hello from chatMe"

    )


    print(note)
