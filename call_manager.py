"""
call_manager.py

chatMe Call Manager

Features:
- Audio calls
- Video calls
- Group calls
- Call history
- Missed calls
- WebRTC signaling support

Used by:
- server.py
- websocket_manager.py
- app.js
"""


import uuid
import datetime



# =====================================
# CALL STORAGE
# =====================================


active_calls = {}

call_history = {}

group_rooms = {}





# =====================================
# CREATE PRIVATE CALL
# =====================================


def create_call(

    caller,

    receiver,

    call_type="audio"

):


    """
    Create private call request
    """



    call_id = str(

        uuid.uuid4()

    )



    call = {


        "id":call_id,


        "caller":caller,


        "receiver":receiver,


        "type":call_type,


        "status":"ringing",


        "created":

        str(datetime.datetime.now())


    }



    active_calls[call_id] = call



    return call






# =====================================
# ACCEPT CALL
# =====================================


def accept_call(

    call_id

):


    if call_id in active_calls:


        active_calls[call_id]["status"] = "connected"


        return active_calls[call_id]



    return None






# =====================================
# REJECT CALL
# =====================================


def reject_call(

    call_id

):


    if call_id in active_calls:


        active_calls[call_id]["status"] = "rejected"



        save_call_history(

            active_calls[call_id]

        )


        del active_calls[call_id]



        return True



    return False





# =====================================
# END CALL
# =====================================


def end_call(

    call_id

):


    if call_id in active_calls:


        active_calls[call_id]["status"] = "ended"



        active_calls[call_id]["ended"] = (

            str(datetime.datetime.now())

        )



        save_call_history(

            active_calls[call_id]

        )



        del active_calls[call_id]



        return True



    return False





# =====================================
# MISSED CALL
# =====================================


def missed_call(

    caller,

    receiver,

    call_type="audio"

):


    call = {


        "caller":caller,


        "receiver":receiver,


        "type":call_type,


        "status":"missed",


        "time":

        str(datetime.datetime.now())


    }



    save_call_history(

        call

    )


    return call






# =====================================
# SAVE CALL HISTORY
# =====================================


def save_call_history(

    call

):


    user = call["caller"]



    if user not in call_history:


        call_history[user] = []



    call_history[user].append(

        call

    )






# =====================================
# GET USER CALL HISTORY
# =====================================


def get_call_history(

    username

):


    return call_history.get(

        username,

        []

    )






# =====================================
# CREATE GROUP CALL ROOM
# =====================================


def create_group_room(

    creator

):


    room_id = str(

        uuid.uuid4()

    )



    group_rooms[room_id] = {


        "creator":creator,


        "users":[creator],


        "created":

        str(datetime.datetime.now())


    }



    return group_rooms[room_id]






# =====================================
# JOIN GROUP ROOM
# =====================================


def join_group_room(

    room_id,

    username

):


    if room_id not in group_rooms:


        return False



    if username not in group_rooms[room_id]["users"]:


        group_rooms[room_id]["users"].append(

            username

        )



    return group_rooms[room_id]







# =====================================
# LEAVE GROUP ROOM
# =====================================


def leave_group_room(

    room_id,

    username

):


    if room_id in group_rooms:


        if username in group_rooms[room_id]["users"]:


            group_rooms[room_id]["users"].remove(

                username

            )


        return True



    return False






# =====================================
# GET ROOM USERS
# =====================================


def get_room_users(

    room_id

):


    if room_id in group_rooms:


        return group_rooms[room_id]["users"]



    return []






# =====================================
# WEBRTC SIGNAL MESSAGE
# =====================================


def create_signal(

    sender,

    receiver,

    signal_type,

    data

):


    """
    Used for:

    offer
    answer
    candidate

    """



    return {


        "type":signal_type,


        "sender":sender,


        "receiver":receiver,


        "data":data


    }






# =====================================
# TEST
# =====================================


if __name__ == "__main__":


    call = create_call(

        "elvis",

        "john",

        "video"

    )


    print(call)



    accept_call(

        call["id"]

    )


    print(

        active_calls

    )
