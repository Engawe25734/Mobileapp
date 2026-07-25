"""
message_manager.py

chatMe Message Manager

Features:
- Message creation
- Message editing
- Message deletion
- Reply messages
- Forward messages
- Message status
- File attachments
- Message search

Used by:
- server.py
- database.py
- websocket_manager.py
"""


import uuid
import datetime





# =====================================
# MESSAGE STORAGE
# =====================================


messages = {}






# =====================================
# CREATE MESSAGE
# =====================================


def create_message(

    sender,

    receiver,

    text,

    attachment=None

):


    """
    Create new chat message
    """



    message_id = str(

        uuid.uuid4()

    )



    message = {


        "id":message_id,


        "sender":sender,


        "receiver":receiver,


        "text":text,


        "attachment":attachment,


        "status":"sent",


        "reply_to":None,


        "created":

        str(datetime.datetime.now()),


        "edited":False


    }




    messages[message_id] = message



    return message






# =====================================
# EDIT MESSAGE
# =====================================


def edit_message(

    message_id,

    new_text

):


    """
    Edit existing message
    """



    if message_id not in messages:


        return None




    messages[message_id]["text"] = new_text



    messages[message_id]["edited"] = True



    messages[message_id]["edited_time"] = (

        str(datetime.datetime.now())

    )



    return messages[message_id]






# =====================================
# DELETE MESSAGE
# =====================================


def delete_message(

    message_id

):


    """
    Delete message
    """



    if message_id in messages:


        del messages[message_id]


        return True



    return False






# =====================================
# REPLY TO MESSAGE
# =====================================


def reply_message(

    message_id,

    sender,

    receiver,

    text

):


    """
    Create reply message
    """



    reply = create_message(

        sender,

        receiver,

        text

    )



    reply["reply_to"] = message_id



    return reply






# =====================================
# FORWARD MESSAGE
# =====================================


def forward_message(

    message_id,

    new_sender,

    new_receiver

):


    """
    Forward existing message
    """



    if message_id not in messages:


        return None




    original = messages[message_id]



    forwarded = create_message(

        new_sender,

        new_receiver,

        original["text"],

        original["attachment"]

    )



    forwarded["forwarded"] = True



    forwarded["original_id"] = message_id



    return forwarded






# =====================================
# MESSAGE STATUS
# =====================================


def update_status(

    message_id,

    status

):


    """
    Status:

    sent
    delivered
    read
    """



    if message_id in messages:


        messages[message_id]["status"] = status


        return messages[message_id]



    return None





# =====================================
# ATTACH FILE
# =====================================


def attach_file(

    message_id,

    file_data

):


    """
    Attach uploaded file
    """



    if message_id in messages:


        messages[message_id]["attachment"] = file_data



        return True



    return False






# =====================================
# GET MESSAGE
# =====================================


def get_message(

    message_id

):


    return messages.get(

        message_id

    )







# =====================================
# GET USER CHAT
# =====================================


def get_conversation(

    user1,

    user2

):


    result = []



    for message in messages.values():


        if (

            message["sender"] == user1

            and

            message["receiver"] == user2

        ) or (

            message["sender"] == user2

            and

            message["receiver"] == user1

        ):


            result.append(

                message

            )



    return result







# =====================================
# SEARCH MESSAGES
# =====================================


def search_messages(

    username,

    keyword

):


    """
    Search user's messages
    """



    results = []



    for message in messages.values():


        if username in [

            message["sender"],

            message["receiver"]

        ]:


            if keyword.lower() in message["text"].lower():


                results.append(

                    message

                )



    return results







# =====================================
# CLEAR CHAT
# =====================================


def clear_conversation(

    user1,

    user2

):


    deleted = []



    for message_id, message in list(messages.items()):


        if (

            message["sender"] == user1

            and

            message["receiver"] == user2

        ) or (

            message["sender"] == user2

            and

            message["receiver"] == user1

        ):


            deleted.append(

                message_id

            )


            del messages[message_id]



    return deleted






# =====================================
# TEST
# =====================================


if __name__ == "__main__":


    msg = create_message(

        "elvis",

        "john",

        "Hello from chatMe"

    )



    print(msg)



    edit_message(

        msg["id"],

        "Updated message"

    )



    print(

        get_message(

            msg["id"]

        )

    )
