"""
database.py

Database manager for Mobile Chat App.

Supports:
- Users
- Private chats
- Messages
- Attachments
- Groups
- Group members
- Group audio/video call rooms
"""


import sqlite3
from datetime import datetime



DATABASE_FILE = "chat.db"



# ==============================
# Connection
# ==============================

def get_connection():

    conn = sqlite3.connect(
        DATABASE_FILE,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn




# ==============================
# Initialize Database
# ==============================

def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE NOT NULL,

        phone TEXT UNIQUE NOT NULL,

        password_hash TEXT NOT NULL,

        online INTEGER DEFAULT 0,

        last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,

        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)



    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_one INTEGER,

        user_two INTEGER,

        created_at DATETIME DEFAULT CURRENT_TIMESTAMP

    )
    """)



    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        chat_id INTEGER,

        sender_id INTEGER,

        message TEXT,

        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP

    )
    """)




    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attachments(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        message_id INTEGER,

        filename TEXT,

        filepath TEXT,

        filetype TEXT,

        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP

    )
    """)




    # GROUPS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS groups(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT NOT NULL,

        created_by INTEGER,

        created_at DATETIME DEFAULT CURRENT_TIMESTAMP

    )
    """)



    cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_members(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        group_id INTEGER,

        user_id INTEGER

    )
    """)




    # VIDEO CALL ROOMS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS call_rooms(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        room_name TEXT UNIQUE,

        created_by INTEGER,

        created_at DATETIME DEFAULT CURRENT_TIMESTAMP

    )
    """)



    cursor.execute("""
    CREATE TABLE IF NOT EXISTS call_participants(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        room_id INTEGER,

        user_id INTEGER,

        joined_at DATETIME DEFAULT CURRENT_TIMESTAMP

    )
    """)



    conn.commit()

    conn.close()


    print("✅ Database initialized successfully")






# ==============================
# Users
# ==============================


def create_user(username, phone, password_hash):

    conn=get_connection()

    cursor=conn.cursor()


    cursor.execute(
        """
        INSERT INTO users
        (
        username,
        phone,
        password_hash
        )
        VALUES(?,?,?)
        """,
        (
            username,
            phone,
            password_hash
        )
    )


    conn.commit()


    user_id=cursor.lastrowid


    conn.close()


    return user_id





def get_user_by_username(username):

    conn=get_connection()

    cursor=conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username=?
        """,
        (username,)
    )


    user=cursor.fetchone()


    conn.close()


    return user






def get_user_by_phone(phone):

    conn=get_connection()

    cursor=conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE phone=?
        """,
        (phone,)
    )


    user=cursor.fetchone()


    conn.close()


    return user






# ==============================
# Private Chat
# ==============================


def get_or_create_chat(user_one,user_two):

    conn=get_connection()

    cursor=conn.cursor()



    cursor.execute(
        """
        SELECT id FROM chats
        WHERE
        (user_one=? AND user_two=?)
        OR
        (user_one=? AND user_two=?)
        """,
        (
            user_one,
            user_two,
            user_two,
            user_one
        )
    )


    chat=cursor.fetchone()



    if chat:

        conn.close()

        return chat["id"]




    cursor.execute(
        """
        INSERT INTO chats
        (user_one,user_two)

        VALUES(?,?)
        """,
        (
            user_one,
            user_two
        )
    )



    conn.commit()


    chat_id=cursor.lastrowid


    conn.close()


    return chat_id





def save_message(chat_id,sender_id,message):

    conn=get_connection()

    cursor=conn.cursor()



    cursor.execute(
        """
        INSERT INTO messages
        (
        chat_id,
        sender_id,
        message
        )
        VALUES(?,?,?)
        """,
        (
            chat_id,
            sender_id,
            message
        )
    )



    conn.commit()


    msg_id=cursor.lastrowid


    conn.close()


    return msg_id





def get_user_messages(user_one,user_two):

    chat_id=get_or_create_chat(
        user_one,
        user_two
    )


    conn=get_connection()

    cursor=conn.cursor()


    cursor.execute(
        """
        SELECT
        users.username,
        messages.message,
        messages.timestamp

        FROM messages

        JOIN users

        ON users.id=messages.sender_id

        WHERE chat_id=?

        ORDER BY timestamp

        """,
        (chat_id,)
    )


    data=cursor.fetchall()


    conn.close()


    return data





# ==============================
# Groups
# ==============================


def create_group(name,creator_id):

    conn=get_connection()

    cursor=conn.cursor()


    cursor.execute(
        """
        INSERT INTO groups
        (name,created_by)

        VALUES(?,?)
        """,
        (
            name,
            creator_id
        )
    )


    conn.commit()


    group_id=cursor.lastrowid


    conn.close()


    add_group_member(
        group_id,
        creator_id
    )


    return group_id





def add_group_member(group_id,user_id):

    conn=get_connection()

    cursor=conn.cursor()


    cursor.execute(
        """
        INSERT INTO group_members
        (group_id,user_id)

        VALUES(?,?)
        """,
        (
            group_id,
            user_id
        )
    )


    conn.commit()

    conn.close()





def get_group_members(group_id):

    conn=get_connection()

    cursor=conn.cursor()


    cursor.execute(
        """
        SELECT users.username

        FROM group_members

        JOIN users

        ON users.id=group_members.user_id

        WHERE group_id=?

        """,
        (group_id,)
    )


    users=cursor.fetchall()


    conn.close()


    return users






# ==============================
# Group Call Rooms
# ==============================


def create_call_room(room_name,user_id):

    conn=get_connection()

    cursor=conn.cursor()


    cursor.execute(
        """
        INSERT INTO call_rooms
        (
        room_name,
        created_by
        )

        VALUES(?,?)
        """,
        (
            room_name,
            user_id
        )
    )


    conn.commit()


    room_id=cursor.lastrowid


    conn.close()


    return room_id






def join_call_room(room_id,user_id):

    conn=get_connection()

    cursor=conn.cursor()


    cursor.execute(
        """
        INSERT INTO call_participants
        (
        room_id,
        user_id
        )

        VALUES(?,?)
        """,
        (
            room_id,
            user_id
        )
    )


    conn.commit()

    conn.close()






def leave_call_room(room_id,user_id):

    conn=get_connection()

    cursor=conn.cursor()


    cursor.execute(
        """
        DELETE FROM call_participants

        WHERE room_id=?
        AND user_id=?

        """,
        (
            room_id,
            user_id
        )
    )


    conn.commit()

    conn.close()




# ==============================
# Attachments
# ==============================


def save_attachment(
    message_id,
    filename,
    filepath,
    filetype
):

    conn=get_connection()

    cursor=conn.cursor()


    cursor.execute(
        """
        INSERT INTO attachments
        (
        message_id,
        filename,
        filepath,
        filetype
        )

        VALUES(?,?,?,?)
        """,
        (
            message_id,
            filename,
            filepath,
            filetype
        )
    )


    conn.commit()

    conn.close()





if __name__=="__main__":

    initialize_database()
