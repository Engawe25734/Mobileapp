"""
database.py

ChatMe Mobile Chat Application Database Manager

Features:
- Users
- Authentication data
- Private chats
- Messages
- Attachments
- User profiles
- Profile pictures
- Groups
- Group members
- Group messages
- Audio/video call rooms
- Block system
- Report system
"""


import sqlite3



DATABASE_FILE = "chat.db"



# =====================================
# DATABASE CONNECTION
# =====================================


def get_connection():

    conn = sqlite3.connect(

        DATABASE_FILE,

        check_same_thread=False

    )


    # Return rows as dictionaries

    conn.row_factory = sqlite3.Row


    # Enable foreign keys

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )


    return conn





# =====================================
# DATABASE INITIALIZATION
# =====================================


def initialize_database():


    conn = get_connection()

    cursor = conn.cursor()



    # =====================================
    # USERS TABLE
    # =====================================

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


    cursor.execute(
        "PRAGMA table_info(users)"
    )

    columns = [

        column[1]

        for column in cursor.fetchall()

    ]


    if "avatar" not in columns:

        cursor.execute("""
        ALTER TABLE users
        ADD COLUMN avatar TEXT DEFAULT '/static/default-avatar.png'
        """)


    if "bio" not in columns:

        cursor.execute("""
        ALTER TABLE users
        ADD COLUMN bio TEXT DEFAULT ''
        """)

    # =====================================
    # PUBLIC KEY TABLE
    # =====================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_keys(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE,

        public_key TEXT,

        FOREIGN KEY(username)

        REFERENCES users(username)

    )
    """)
    # =====================================
    # PRIVATE CHAT TABLE
    # =====================================


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_one INTEGER NOT NULL,

        user_two INTEGER NOT NULL,

        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,


        FOREIGN KEY(user_one)

        REFERENCES users(id),


        FOREIGN KEY(user_two)

        REFERENCES users(id)

    )
    """)





    # =====================================
    # PRIVATE MESSAGE TABLE
    # =====================================


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(

        id INTEGER PRIMARY KEY AUTOINCREMENT,


        chat_id INTEGER NOT NULL,


        sender_id INTEGER NOT NULL,


        message TEXT,


        message_type TEXT DEFAULT 'text',


        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,


        FOREIGN KEY(chat_id)

        REFERENCES chats(id),


        FOREIGN KEY(sender_id)

        REFERENCES users(id)

    )
    """)





    # =====================================
    # ATTACHMENTS TABLE
    # =====================================


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attachments(

        id INTEGER PRIMARY KEY AUTOINCREMENT,


        message_id INTEGER,


        filename TEXT NOT NULL,


        filepath TEXT,


        file_url TEXT,


        filetype TEXT,


        filesize INTEGER DEFAULT 0,


        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,


        FOREIGN KEY(message_id)

        REFERENCES messages(id)

    )
    """)





    # =====================================
    # USER PROFILE TABLE
    # =====================================


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles(

        id INTEGER PRIMARY KEY AUTOINCREMENT,


        user_id INTEGER UNIQUE,


        avatar TEXT DEFAULT '',


        bio TEXT DEFAULT '',


        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,


        FOREIGN KEY(user_id)

        REFERENCES users(id)

    )
    """)





    # =====================================
    # GROUP TABLE
    # =====================================


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS groups(

        id INTEGER PRIMARY KEY AUTOINCREMENT,


        name TEXT NOT NULL,


        created_by INTEGER,


        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,


        FOREIGN KEY(created_by)

        REFERENCES users(id)

    )
    """)





    # =====================================
    # GROUP MEMBERS TABLE
    # =====================================


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_members(

        id INTEGER PRIMARY KEY AUTOINCREMENT,


        group_id INTEGER,


        user_id INTEGER,


        FOREIGN KEY(group_id)

        REFERENCES groups(id),


        FOREIGN KEY(user_id)

        REFERENCES users(id)

    )
    """)





    # =====================================
    # GROUP MESSAGE TABLE
    # =====================================


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS group_messages(

        id INTEGER PRIMARY KEY AUTOINCREMENT,


        group_id INTEGER,


        sender_id INTEGER,


        message TEXT,


        message_type TEXT DEFAULT 'text',


        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,


        FOREIGN KEY(group_id)

        REFERENCES groups(id),


        FOREIGN KEY(sender_id)

        REFERENCES users(id)

    )
    """)





    # =====================================
    # CALL ROOMS TABLE
    # =====================================


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS call_rooms(

        id INTEGER PRIMARY KEY AUTOINCREMENT,


        room_name TEXT UNIQUE NOT NULL,


        created_by INTEGER,


        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,


        FOREIGN KEY(created_by)

        REFERENCES users(id)

    )
    """)





    # =====================================
    # CALL PARTICIPANTS TABLE
    # =====================================


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS call_participants(

        id INTEGER PRIMARY KEY AUTOINCREMENT,


        room_id INTEGER,


        user_id INTEGER,


        joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,


        FOREIGN KEY(room_id)

        REFERENCES call_rooms(id),


        FOREIGN KEY(user_id)

        REFERENCES users(id)

    )
    """)





    # =====================================
    # BLOCK SYSTEM
    # =====================================


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blocked_users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,


        blocker_id INTEGER,


        blocked_id INTEGER,


        created_at DATETIME DEFAULT CURRENT_TIMESTAMP

    )
    """)
    




    # =====================================
    # REPORT SYSTEM
    # =====================================


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports(

        id INTEGER PRIMARY KEY AUTOINCREMENT,


        reporter_id INTEGER,


        reported_user INTEGER,


        reason TEXT,


        created_at DATETIME DEFAULT CURRENT_TIMESTAMP

    )
    """)
    
# =====================================
# PROFILE SETTINGS TABLE
# =====================================


    # =====================================
    # PROFILE SETTINGS TABLE
    # =====================================


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profile_settings(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER UNIQUE,

        privacy_last_seen TEXT DEFAULT 'Everyone',

        privacy_online_status TEXT DEFAULT 'Everyone',

        privacy_picture TEXT DEFAULT 'Everyone',

        read_receipts INTEGER DEFAULT 1,

        typing_indicator INTEGER DEFAULT 1,

        message_notifications INTEGER DEFAULT 1,

        call_notifications INTEGER DEFAULT 1,

        group_notifications INTEGER DEFAULT 1,

        theme TEXT DEFAULT 'light',

        FOREIGN KEY(user_id)

        REFERENCES users(id)

    )
    """)



    conn.commit()

    conn.close()



    print(
        "✅ ChatMe database initialized successfully"
    )
    
# =====================================
# USER MANAGEMENT
# =====================================


def create_user(

    username,

    phone,

    password_hash

):


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(

    """

    INSERT INTO users

    (username,phone,password_hash)

    VALUES (?,?,?)

    """,

    (

        username,

        phone,

        password_hash

    )

    )


    user_id = cursor.lastrowid



    cursor.execute(

    """

    INSERT INTO profile_settings

    (user_id)

    VALUES (?)

    """,

    (

        user_id,

    )

    )


    conn.commit()

    conn.close()


    return user_id





def get_user_by_username(

    username

):


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





def get_user_by_phone(

    phone

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        SELECT *

        FROM users

        WHERE phone=?

        """,

        (

            phone,

        )

    )



    user = cursor.fetchone()



    conn.close()



    return user





def update_user_status(

    username,

    status

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        UPDATE users

        SET

        online=?,

        last_seen=CURRENT_TIMESTAMP


        WHERE username=?

        """,

        (

            status,

            username

        )

    )



    conn.commit()

    conn.close()







# =====================================
# USER PROFILE SYSTEM
# =====================================


def create_profile(

    user_id

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        INSERT OR IGNORE INTO profiles

        (

        user_id

        )

        VALUES(?)

        """,

        (

            user_id,

        )

    )



    conn.commit()

    conn.close()





def get_profile(

    username

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        SELECT


        users.username,


        users.phone,


        profiles.avatar,


        profiles.bio



        FROM users



        LEFT JOIN profiles



        ON users.id = profiles.user_id



        WHERE users.username=?


        """,

        (

            username,

        )

    )



    profile = cursor.fetchone()



    conn.close()



    return profile





def update_profile_picture(

    user_id,

    avatar

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        UPDATE profiles


        SET


        avatar=?,


        updated_at=CURRENT_TIMESTAMP



        WHERE user_id=?


        """,

        (

            avatar,

            user_id

        )

    )



    conn.commit()

    conn.close()





def update_profile_bio(

    user_id,

    bio

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        UPDATE profiles


        SET


        bio=?,


        updated_at=CURRENT_TIMESTAMP



        WHERE user_id=?


        """,

        (

            bio,

            user_id

        )

    )



    conn.commit()

    conn.close()







# =====================================
# BLOCK SYSTEM
# =====================================


def block_user(

    blocker_id,

    blocked_id

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        INSERT INTO blocked_users


        (

        blocker_id,

        blocked_id

        )


        VALUES(?,?)

        """,

        (

            blocker_id,

            blocked_id

        )

    )



    conn.commit()

    conn.close()





def unblock_user(

    blocker_id,

    blocked_id

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        DELETE FROM blocked_users


        WHERE blocker_id=?


        AND blocked_id=?


        """,

        (

            blocker_id,

            blocked_id

        )

    )



    conn.commit()

    conn.close()





def is_blocked(

    user_one,

    user_two

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        SELECT id

        FROM blocked_users


        WHERE


        (blocker_id=? AND blocked_id=?)


        OR


        (blocker_id=? AND blocked_id=?)



        """,

        (

            user_one,

            user_two,

            user_two,

            user_one

        )

    )



    result = cursor.fetchone()



    conn.close()



    return result is not None







# =====================================
# REPORT SYSTEM
# =====================================


def report_user(

    reporter_id,

    reported_user,

    reason

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        INSERT INTO reports


        (

        reporter_id,

        reported_user,

        reason

        )


        VALUES(?,?,?)


        """,

        (

            reporter_id,

            reported_user,

            reason

        )

    )



    conn.commit()

    conn.close()
    # =====================================
# PRIVATE CHAT MANAGEMENT
# =====================================


def get_or_create_chat(

    user_one,

    user_two

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        SELECT id

        FROM chats


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



    chat = cursor.fetchone()



    if chat:


        conn.close()


        return chat["id"]





    cursor.execute(

        """

        INSERT INTO chats


        (

        user_one,

        user_two

        )


        VALUES(?,?)


        """,

        (

            user_one,

            user_two

        )

    )



    conn.commit()



    chat_id = cursor.lastrowid



    conn.close()



    return chat_id







# =====================================
# SAVE PRIVATE MESSAGE
# =====================================


def save_message(

    chat_id,

    sender_id,

    message,

    message_type="text"

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        INSERT INTO messages


        (

        chat_id,

        sender_id,

        message,

        message_type

        )


        VALUES(?,?,?,?)


        """,

        (

            chat_id,

            sender_id,

            message,

            message_type

        )

    )



    conn.commit()



    message_id = cursor.lastrowid



    conn.close()



    return message_id







# =====================================
# LOAD MESSAGE HISTORY
# =====================================


def get_user_messages(

    user_one,

    user_two

):


    chat_id = get_or_create_chat(

        user_one,

        user_two

    )



    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        SELECT


        users.username,


        messages.id,


        messages.message,


        messages.message_type,


        messages.timestamp



        FROM messages



        JOIN users



        ON users.id = messages.sender_id



        WHERE messages.chat_id=?



        ORDER BY messages.timestamp ASC



        """,

        (

            chat_id,

        )

    )



    messages = cursor.fetchall()



    conn.close()



    return messages







# =====================================
# SAVE ATTACHMENT
# =====================================


def save_attachment(

    message_id,

    filename,

    filepath,

    file_url,

    filetype,

    filesize=0

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        INSERT INTO attachments


        (

        message_id,

        filename,

        filepath,

        file_url,

        filetype,

        filesize

        )


        VALUES(?,?,?,?,?,?)


        """,

        (

            message_id,

            filename,

            filepath,

            file_url,

            filetype,

            filesize

        )

    )



    conn.commit()



    attachment_id = cursor.lastrowid



    conn.close()



    return attachment_id







# =====================================
# GET MESSAGE ATTACHMENTS
# =====================================


def get_message_attachments(

    message_id

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        SELECT *


        FROM attachments



        WHERE message_id=?



        """,

        (

            message_id,

        )

    )



    files = cursor.fetchall()



    conn.close()



    return files







# =====================================
# SAVE FILE MESSAGE
# =====================================


def save_file_message(

    chat_id,

    sender_id,

    filename,

    filepath,

    file_url,

    filetype,

    filesize

):


    message_id = save_message(

        chat_id,

        sender_id,

        filename,

        filetype

    )



    save_attachment(

        message_id,

        filename,

        filepath,

        file_url,

        filetype,

        filesize

    )



    return message_id







# =====================================
# GROUP MANAGEMENT
# =====================================


def create_group(

    name,

    creator_id

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        INSERT INTO groups


        (

        name,

        created_by

        )


        VALUES(?,?)


        """,

        (

            name,

            creator_id

        )

    )



    conn.commit()



    group_id = cursor.lastrowid



    conn.close()



    add_group_member(

        group_id,

        creator_id

    )



    return group_id







def add_group_member(

    group_id,

    user_id

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        INSERT INTO group_members


        (

        group_id,

        user_id

        )


        SELECT ?,?



        WHERE NOT EXISTS



        (



        SELECT id

        FROM group_members



        WHERE group_id=?

        AND user_id=?



        )


        """,

        (

            group_id,

            user_id,

            group_id,

            user_id

        )

    )



    conn.commit()



    conn.close()







def get_group_members(

    group_id

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        SELECT users.username



        FROM group_members



        JOIN users



        ON users.id = group_members.user_id



        WHERE group_id=?



        """,

        (

            group_id,

        )

    )



    members = cursor.fetchall()



    conn.close()



    return members







# =====================================
# GROUP MESSAGE SYSTEM
# =====================================


def save_group_message(

    group_id,

    sender_id,

    message,

    message_type="text"

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        INSERT INTO group_messages


        (

        group_id,

        sender_id,

        message,

        message_type

        )


        VALUES(?,?,?,?)


        """,

        (

            group_id,

            sender_id,

            message,

            message_type

        )

    )



    conn.commit()



    message_id = cursor.lastrowid



    conn.close()



    return message_id
    # =====================================
# AUDIO / VIDEO CALL ROOMS
# =====================================


def create_call_room(

    room_name,

    created_by

):


    conn = get_connection()

    cursor = conn.cursor()



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

            created_by

        )

    )



    conn.commit()



    room_id = cursor.lastrowid



    conn.close()



    return room_id







def get_call_room(

    room_name

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        SELECT *

        FROM call_rooms


        WHERE room_name=?



        """,

        (

            room_name,

        )

    )



    room = cursor.fetchone()



    conn.close()



    return room







def join_call_room(

    room_id,

    user_id

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        INSERT INTO call_participants


        (

        room_id,

        user_id

        )


        SELECT ?,?



        WHERE NOT EXISTS



        (


        SELECT id

        FROM call_participants


        WHERE room_id=?

        AND user_id=?


        )


        """,

        (

            room_id,

            user_id,

            room_id,

            user_id

        )

    )



    conn.commit()



    conn.close()







def leave_call_room(

    room_id,

    user_id

):


    conn = get_connection()

    cursor = conn.cursor()



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







def get_call_participants(

    room_id

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        SELECT


        users.username



        FROM call_participants



        JOIN users



        ON users.id = call_participants.user_id



        WHERE room_id=?



        """,

        (

            room_id,

        )

    )



    users = cursor.fetchall()



    conn.close()



    return users







# =====================================
# DELETE CHAT HISTORY
# =====================================


def delete_chat_messages(

    chat_id

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        DELETE FROM messages


        WHERE chat_id=?


        """,

        (

            chat_id,

        )

    )



    conn.commit()



    conn.close()

# =====================================
# UPDATE PROFILE PICTURE
# =====================================


def update_profile_picture(

    user_id,

    image_url

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

    """

    UPDATE users

    SET avatar=?

    WHERE id=?

    """,

    (

        image_url,

        user_id

    )

    )



    conn.commit()

    conn.close()

# =====================================
# UPDATE PRIVACY SETTINGS
# =====================================


def update_privacy_settings(

    user_id,

    settings

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

    """

    UPDATE profile_settings

    SET

    privacy_last_seen=?,

    privacy_online_status=?,

    privacy_picture=?,

    read_receipts=?,

    typing_indicator=?

    WHERE user_id=?

    """,

    (

        settings.get("last_seen"),

        settings.get("online_status"),

        settings.get("profile_picture"),

        int(settings.get("read_receipts")),

        int(settings.get("typing_indicator")),

        user_id

    )

    )



    conn.commit()

    conn.close()

# =====================================
# UPDATE NOTIFICATIONS
# =====================================


def update_notification_settings(

    user_id,

    settings

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

    """

    UPDATE profile_settings

    SET

    message_notifications=?,

    call_notifications=?,

    group_notifications=?

    WHERE user_id=?

    """,

    (

        int(settings.get("messages")),

        int(settings.get("calls")),

        int(settings.get("groups")),

        user_id

    )

    )


    conn.commit()

    conn.close()

# =====================================
# UPDATE BIO
# =====================================


def update_profile_bio(

    user_id,

    bio

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

    """

    UPDATE users

    SET bio=?

    WHERE id=?

    """,

    (

        bio,

        user_id

    )

    )



    conn.commit()

    conn.close()


# =====================================
# UPDATE THEME
# =====================================


def update_theme(

    user_id,

    theme

):


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(

    """

    UPDATE profile_settings

    SET theme=?

    WHERE user_id=?

    """,

    (

        theme,

        user_id

    )

    )


    conn.commit()

    conn.close()

# =====================================
# GET SETTINGS
# =====================================


def get_profile_settings(

    user_id

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

    """

    SELECT *

    FROM profile_settings

    WHERE user_id=?

    """,

    (

        user_id,

    )

    )



    row = cursor.fetchone()



    conn.close()



    if not row:

        return {}



    return dict(row)
# =====================================
# DATABASE CLEANUP
# =====================================


def close_database():

    conn = get_connection()

    conn.close()







# =====================================
# TEST DATABASE
# =====================================


if __name__ == "__main__":


    initialize_database()



    print(
        "✅ ChatMe database ready"
    )
    
