"""
database_manager.py

chatMe Database Manager

Features:
- SQLite database
- User storage
- Message storage
- File attachments
- Reactions
- Notifications
- Calls
- Contacts

Used by:
- server.py
- auth.py
- message_manager.py
- notifications.py
"""


import sqlite3
import datetime



# =====================================
# DATABASE CONFIGURATION
# =====================================


DATABASE = "chatme.db"





# =====================================
# CONNECTION
# =====================================


def get_connection():

    return sqlite3.connect(

        DATABASE

    )






# =====================================
# INITIALIZE DATABASE
# =====================================


def initialize_database():


    conn = get_connection()

    cursor = conn.cursor()



    # USERS TABLE

    cursor.execute(
    """

    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE,

        phone TEXT UNIQUE,

        password TEXT,

        profile_picture TEXT,

        bio TEXT,

        status TEXT,

        last_seen TEXT,

        created TEXT

    )

    """
    )




    # MESSAGES TABLE

    cursor.execute(
    """

    CREATE TABLE IF NOT EXISTS messages(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        sender TEXT,

        receiver TEXT,

        message TEXT,

        attachment TEXT,

        status TEXT,

        reply_to INTEGER,

        created TEXT,

        edited INTEGER

    )

    """
    )





    # ATTACHMENTS TABLE

    cursor.execute(
    """

    CREATE TABLE IF NOT EXISTS attachments(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        filename TEXT,

        path TEXT,

        file_type TEXT,

        uploaded TEXT

    )

    """
    )





    # REACTIONS TABLE

    cursor.execute(
    """

    CREATE TABLE IF NOT EXISTS reactions(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        message_id INTEGER,

        username TEXT,

        reaction TEXT

    )

    """
    )






    # NOTIFICATIONS TABLE

    cursor.execute(
    """

    CREATE TABLE IF NOT EXISTS notifications(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        receiver TEXT,

        sender TEXT,

        title TEXT,

        message TEXT,

        type TEXT,

        is_read INTEGER,

        created TEXT

    )

    """
    )






    # CALL HISTORY TABLE

    cursor.execute(
    """

    CREATE TABLE IF NOT EXISTS calls(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        caller TEXT,

        receiver TEXT,

        call_type TEXT,

        status TEXT,

        created TEXT

    )

    """
    )






    # CONTACTS TABLE

    cursor.execute(
    """

    CREATE TABLE IF NOT EXISTS contacts(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        contact TEXT

    )

    """
    )



    conn.commit()

    conn.close()



    print(

        "✅ chatMe database initialized"

    )







# =====================================
# USER FUNCTIONS
# =====================================


def create_user(

    username,

    phone,

    password

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

    """

    INSERT INTO users

    (

    username,

    phone,

    password,

    status,

    created

    )

    VALUES(?,?,?,?,?)

    """,

    (

        username,

        phone,

        password,

        "offline",

        str(datetime.datetime.now())

    )

    )



    conn.commit()

    conn.close()






def get_user(username):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

    """

    SELECT *

    FROM users

    WHERE username=?

    """,

    (

        username,

    )

    )



    user = cursor.fetchone()



    conn.close()



    return user






# =====================================
# MESSAGE FUNCTIONS
# =====================================


def save_message(

    sender,

    receiver,

    message,

    attachment=None

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

    """

    INSERT INTO messages

    (

    sender,

    receiver,

    message,

    attachment,

    status,

    created

    )

    VALUES(?,?,?,?,?,?)

    """,

    (

        sender,

        receiver,

        message,

        attachment,

        "sent",

        str(datetime.datetime.now())

    )

    )



    conn.commit()

    conn.close()






def get_messages(

    user1,

    user2

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

    """

    SELECT *

    FROM messages

    WHERE

    (sender=? AND receiver=?)

    OR

    (sender=? AND receiver=?)

    ORDER BY id

    """,

    (

        user1,

        user2,

        user2,

        user1

    )

    )



    data = cursor.fetchall()



    conn.close()



    return data







# =====================================
# REACTION FUNCTIONS
# =====================================


def add_reaction(

    message_id,

    username,

    reaction

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

    """

    INSERT INTO reactions

    VALUES(NULL,?,?,?)

    """,

    (

        message_id,

        username,

        reaction

    )

    )


    conn.commit()

    conn.close()






# =====================================
# NOTIFICATION FUNCTIONS
# =====================================


def save_notification(

    receiver,

    sender,

    title,

    message,

    ntype

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

    """

    INSERT INTO notifications

    VALUES(NULL,?,?,?,?,?,?,?)

    """,

    (

        receiver,

        sender,

        title,

        message,

        ntype,

        0,

        str(datetime.datetime.now())

    )

    )



    conn.commit()

    conn.close()





# =====================================
# CALL HISTORY
# =====================================


def save_call(

    caller,

    receiver,

    call_type,

    status

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

    """

    INSERT INTO calls

    VALUES(NULL,?,?,?,?,?)

    """,

    (

        caller,

        receiver,

        call_type,

        status,

        str(datetime.datetime.now())

    )

    )



    conn.commit()

    conn.close()






# =====================================
# TEST
# =====================================


if __name__ == "__main__":


    initialize_database()
