"""
Server-side database configuration for mobile app.
Creates and manages:
- Users
- Private chats
- Messages
- Groups
- Group members
"""

import sqlite3
from datetime import datetime

DATABASE_FILE = "chat.db"


# ------------------------------------
# Database connection
# ------------------------------------

def get_connection():
"""
Creates a connection to SQLite database.
"""
conn = sqlite3.connect(
DATABASE_FILE,
check_same_thread=False
)

conn.row_factory = sqlite3.Row
return conn


# ------------------------------------
# Initialize database tables
# ------------------------------------

def initialize_database():

conn = get_connection()
cursor = conn.cursor()


# -------------------------------
# Users table
# -------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

id INTEGER PRIMARY KEY AUTOINCREMENT,

username TEXT UNIQUE NOT NULL,

phone TEXT UNIQUE NOT NULL,

password_hash TEXT NOT NULL,

online INTEGER DEFAULT 0,

last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,

created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")


# -------------------------------
# Private conversations
# -------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (

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



# -------------------------------
# Messages table
# -------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (

id INTEGER PRIMARY KEY AUTOINCREMENT,

chat_id INTEGER NOT NULL,

sender_id INTEGER NOT NULL,

message TEXT NOT NULL,

delivered INTEGER DEFAULT 0,

read INTEGER DEFAULT 0,

timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,


FOREIGN KEY(chat_id)
REFERENCES chats(id),


FOREIGN KEY(sender_id)
REFERENCES users(id)

)
""")


# -------------------------------
# Media attachments
# -------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS attachments(

id INTEGER PRIMARY KEY AUTOINCREMENT,

message_id INTEGER,

filename TEXT,

filepath TEXT,

filetype TEXT,

timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,


FOREIGN KEY(message_id)
REFERENCES messages(id)

)
""")
# -------------------------------
# Groups table
# -------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS groups (

id INTEGER PRIMARY KEY AUTOINCREMENT,

name TEXT NOT NULL,

created_by INTEGER NOT NULL,

created_at DATETIME DEFAULT CURRENT_TIMESTAMP,


FOREIGN KEY(created_by)
REFERENCES users(id)

)
""")



# -------------------------------
# Group members
# -------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS group_members (

id INTEGER PRIMARY KEY AUTOINCREMENT,

group_id INTEGER NOT NULL,

user_id INTEGER NOT NULL,


FOREIGN KEY(group_id)
REFERENCES groups(id),


FOREIGN KEY(user_id)
REFERENCES users(id)

)
""")


conn.commit()
conn.close()

print("✅ Database initialized successfully")



# ------------------------------------
# User functions
# ------------------------------------


def create_user(username, phone, password_hash):

conn = get_connection()
cursor = conn.cursor()


cursor.execute("""
INSERT INTO users
(
username,
phone,
password_hash
)

VALUES (?, ?, ?)

""",
(
username,
phone,
password_hash
))


conn.commit()

user_id = cursor.lastrowid

conn.close()

return user_id



def get_user_by_phone(phone):

conn = get_connection()

cursor = conn.cursor()


cursor.execute("""
SELECT *
FROM users
WHERE phone = ?

""",
(phone,))


user = cursor.fetchone()

conn.close()

return user



def update_user_status(user_id, status):

conn = get_connection()

cursor = conn.cursor()


cursor.execute("""
UPDATE users

SET online = ?,
last_seen = ?

WHERE id = ?

""",
(
status,
datetime.now(),
user_id
))


conn.commit()
conn.close()



# ------------------------------------
# Message functions
# ------------------------------------


def save_message(
chat_id,
sender_id,
message
):

conn = get_connection()

cursor = conn.cursor()


cursor.execute("""
INSERT INTO messages
(
chat_id,
sender_id,
message
)

VALUES (?, ?, ?)

""",
(
chat_id,
sender_id,
message
))


conn.commit()

message_id = cursor.lastrowid

conn.close()

return message_id



def get_chat_messages(chat_id):

conn = get_connection()

cursor = conn.cursor()


cursor.execute("""
SELECT
messages.id,
users.username,
messages.message,
messages.delivered,
messages.read,
messages.timestamp

FROM messages

JOIN users

ON messages.sender_id = users.id

WHERE chat_id = ?

ORDER BY timestamp ASC

""",
(chat_id,))


messages = cursor.fetchall()

conn.close()

return messages



# ------------------------------------
# Run database setup
# ------------------------------------

if __name__ == "__main__":

initialize_database()

# ------------------------------------
# Chat functions
# ------------------------------------


def get_or_create_chat(user_one, user_two):

conn = get_connection()

cursor = conn.cursor()


cursor.execute("""
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
))


chat = cursor.fetchone()



if chat:

conn.close()

return chat["id"]



cursor.execute("""
INSERT INTO chats
(
user_one,
user_two
)

VALUES (?,?)

""",
(
user_one,
user_two
))


conn.commit()


chat_id = cursor.lastrowid


conn.close()


return chat_id





def get_user_messages(
user_one,
user_two
):


chat_id = get_or_create_chat(
user_one,
user_two
)


return get_chat_messages(
chat_id
)

def save_attachment(
message_id,
filename,
filepath,
filetype
):

conn = get_connection()

cursor = conn.cursor()


cursor.execute("""
INSERT INTO attachments
(
message_id,
filename,
filepath,
filetype
)

VALUES (?,?,?,?)

""",
(
message_id,
filename,
filepath,
filetype
))
