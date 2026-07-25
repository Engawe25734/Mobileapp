"""
user_manager.py

chatMe User Manager

Features:
- User profile management
- Contact list
- Online status
- Last seen
- User search
- Blocking system
- Account settings

Used by:
- server.py
- database.py
- websocket_manager.py
"""


import datetime
import uuid





# =====================================
# USER STORAGE
# =====================================


users = {}

contacts = {}

blocked_users = {}





# =====================================
# CREATE USER PROFILE
# =====================================


def create_profile(

    username,

    phone

):


    """
    Create chatMe profile
    """



    user_id = str(

        uuid.uuid4()

    )



    profile = {


        "id":user_id,


        "username":username,


        "phone":phone,


        "profile_picture":

        "/static/default-avatar.png",


        "bio":"",


        "status":"offline",


        "last_seen":

        str(datetime.datetime.now()),


        "created":

        str(datetime.datetime.now())


    }



    users[username] = profile



    return profile






# =====================================
# GET USER PROFILE
# =====================================


def get_profile(

    username

):


    return users.get(

        username

    )






# =====================================
# UPDATE PROFILE
# =====================================


def update_profile(

    username,

    data

):


    """
    Update user information
    """



    if username not in users:


        return None



    allowed = [


        "bio",

        "profile_picture",

        "status"


    ]



    for key,value in data.items():


        if key in allowed:


            users[username][key] = value



    return users[username]






# =====================================
# ONLINE STATUS
# =====================================


def set_online(

    username

):


    if username in users:


        users[username]["status"] = "online"

        return True



    return False






def set_offline(

    username

):


    if username in users:


        users[username]["status"] = "offline"



        users[username]["last_seen"] = (

            str(datetime.datetime.now())

        )



        return True



    return False






# =====================================
# LAST SEEN
# =====================================


def get_last_seen(

    username

):


    if username in users:


        return users[username]["last_seen"]



    return None






# =====================================
# SEARCH USERS
# =====================================


def search_users(

    keyword

):


    """
    Search chatMe users
    """



    result = []



    for username,profile in users.items():


        if keyword.lower() in username.lower():


            result.append(

                profile

            )



    return result






# =====================================
# CONTACT MANAGEMENT
# =====================================


def add_contact(

    username,

    contact

):


    if username not in contacts:


        contacts[username] = []



    if contact not in contacts[username]:


        contacts[username].append(

            contact

        )



    return contacts[username]






def remove_contact(

    username,

    contact

):


    if username in contacts:


        if contact in contacts[username]:


            contacts[username].remove(

                contact

            )


            return True



    return False






def get_contacts(

    username

):


    return contacts.get(

        username,

        []

    )






# =====================================
# BLOCK USERS
# =====================================


def block_user(

    username,

    blocked

):


    if username not in blocked_users:


        blocked_users[username] = []



    if blocked not in blocked_users[username]:


        blocked_users[username].append(

            blocked

        )



    return True






def unblock_user(

    username,

    blocked

):


    if username in blocked_users:


        if blocked in blocked_users[username]:


            blocked_users[username].remove(

                blocked

            )


            return True



    return False






def is_blocked(

    username,

    other_user

):


    return other_user in blocked_users.get(

        username,

        []

    )






# =====================================
# ACCOUNT SETTINGS
# =====================================


def account_settings(

    username

):


    """
    Return editable settings
    """



    return {


        "notifications":True,


        "dark_mode":False,


        "privacy":"friends",


        "username":username


    }







# =====================================
# DELETE ACCOUNT
# =====================================


def delete_account(

    username

):


    if username in users:


        del users[username]


        if username in contacts:


            del contacts[username]


        return True



    return False






# =====================================
# TEST
# =====================================


if __name__ == "__main__":


    user = create_profile(

        "elvis",

        "+237000000000"

    )


    print(user)



    set_online(

        "elvis"

    )


    print(

        get_profile(

            "elvis"

        )

    )
