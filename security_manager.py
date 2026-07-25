"""
security_manager.py

chatMe Security Manager

Features:
- Password encryption
- JWT authentication
- Session control
- Login protection
- User blocking
- User reporting

Used by:
- auth.py
- server.py
- database.py
"""


import hashlib
import secrets
import datetime
import jwt



# =====================================
# CONFIGURATION
# =====================================


SECRET_KEY = "chatMe_secret_key_change_this"


ALGORITHM = "HS256"



# =====================================
# SECURITY STORAGE
# =====================================


active_sessions = {}

failed_attempts = {}

blocked_users = {}

reports = {}





# =====================================
# PASSWORD HASHING
# =====================================


def hash_password(password):


    """
    Secure password hashing
    """



    salt = secrets.token_hex(16)



    hashed = hashlib.sha256(

        (

            password +

            salt

        ).encode()

    ).hexdigest()



    return {


        "hash":hashed,


        "salt":salt


    }







# =====================================
# VERIFY PASSWORD
# =====================================


def verify_password(

    password,

    stored_hash,

    salt

):


    check = hashlib.sha256(

        (

            password +

            salt

        ).encode()

    ).hexdigest()



    return check == stored_hash





# =====================================
# CREATE JWT TOKEN
# =====================================


def create_token(

    user_id,

    username

):


    payload = {


        "user_id":user_id,


        "username":username,


        "created":

        str(datetime.datetime.now()),



        "exp":

        datetime.datetime.utcnow()

        +

        datetime.timedelta(hours=24)

    }



    token = jwt.encode(

        payload,

        SECRET_KEY,

        algorithm=ALGORITHM

    )



    return token





# =====================================
# VERIFY TOKEN
# =====================================


def verify_token(

    token

):


    try:


        data = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[ALGORITHM]

        )


        return data



    except Exception:


        return None





# =====================================
# CREATE SESSION
# =====================================


def create_session(

    username,

    token

):


    active_sessions[username] = {


        "token":token,


        "login_time":

        str(datetime.datetime.now())


    }


    return True





# =====================================
# REMOVE SESSION
# =====================================


def logout(

    username

):


    if username in active_sessions:


        del active_sessions[username]


        return True



    return False






# =====================================
# FAILED LOGIN TRACKING
# =====================================


def record_failed_login(

    username

):


    if username not in failed_attempts:


        failed_attempts[username] = 0



    failed_attempts[username] += 1



    return failed_attempts[username]






def reset_failed_login(

    username

):


    if username in failed_attempts:


        del failed_attempts[username]





def is_login_blocked(

    username

):


    return (

        failed_attempts.get(

            username,

            0

        )

        >=

        5

    )





# =====================================
# BLOCK USER
# =====================================


def block_user(

    blocker,

    blocked

):


    if blocker not in blocked_users:


        blocked_users[blocker] = []



    blocked_users[blocker].append(

        blocked

    )



    return True






def unblock_user(

    blocker,

    blocked

):


    if blocker in blocked_users:


        if blocked in blocked_users[blocker]:


            blocked_users[blocker].remove(

                blocked

            )


            return True



    return False






def is_blocked(

    user1,

    user2

):


    return (

        user2 in blocked_users.get(

            user1,

            []

        )

    )






# =====================================
# REPORT USER
# =====================================


def report_user(

    reporter,

    reported,

    reason

):


    report_id = secrets.token_hex(8)



    reports[report_id] = {


        "reporter":reporter,


        "reported":reported,


        "reason":reason,


        "time":

        str(datetime.datetime.now())


    }



    return reports[report_id]






# =====================================
# SECURITY LOG
# =====================================


def security_log(

    username,

    action

):


    print(

        {

            "user":username,


            "action":action,


            "time":

            str(datetime.datetime.now())

        }

    )





# =====================================
# TEST
# =====================================


if __name__ == "__main__":


    password = hash_password(

        "password123"

    )


    print(password)



    print(

        verify_password(

            "password123",

            password["hash"],

            password["salt"]

        )

    )


    token = create_token(

        1,

        "elvis"

    )


    print(token)
