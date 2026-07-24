"""
local_storage.py

Local SQLite storage engine
for mobile client.

Stores:
- Messages
- Offline queue
- Sync status
"""


import sqlite3
from datetime import datetime



DATABASE = "phone_storage.db"



# ------------------------------------
# Database initialization
# ------------------------------------

def init_storage():

conn = sqlite3.connect(
DATABASE
)

cursor = conn.cursor()



cursor.execute("""
CREATE TABLE IF NOT EXISTS messages(

id INTEGER PRIMARY KEY AUTOINCREMENT,

sender TEXT,

receiver TEXT,

message TEXT,

status TEXT,

timestamp DATETIME

)
""")



cursor.execute("""
CREATE TABLE IF NOT EXISTS offline_queue(

id INTEGER PRIMARY KEY AUTOINCREMENT,

receiver TEXT,

message TEXT,

timestamp DATETIME

)
""")



conn.commit()

conn.close()



print(
"📱 Local phone storage ready"
)





# ------------------------------------
# Save received message
# ------------------------------------

def save_message(
sender,
receiver,
message
):

conn = sqlite3.connect(
DATABASE
)

cursor = conn.cursor()


cursor.execute("""
INSERT INTO messages
(
sender,
receiver,
message,
status,
timestamp
)

VALUES(?,?,?,?,?)

""",
(
sender,
receiver,
message,
"received",
datetime.now()
))


conn.commit()

conn.close()





# ------------------------------------
# Save offline message
# ------------------------------------

def save_offline_message(
receiver,
message
):

conn = sqlite3.connect(
DATABASE
)

cursor = conn.cursor()


cursor.execute("""
INSERT INTO offline_queue
(
receiver,
message,
timestamp
)

VALUES(?,?,?)

""",
(
receiver,
message,
datetime.now()
))


conn.commit()

conn.close()



print(
"💾 Message stored offline"
)





# ------------------------------------
# Get queued messages
# ------------------------------------

def get_offline_messages():


conn = sqlite3.connect(
DATABASE
)


cursor = conn.cursor()


cursor.execute(
"""
SELECT *
FROM offline_queue
ORDER BY id
"""
)


messages = cursor.fetchall()


conn.close()


return messages





# ------------------------------------
# Delete sent queue item
# ------------------------------------

def remove_offline_message(
message_id
):

conn = sqlite3.connect(
DATABASE
)


cursor = conn.cursor()


cursor.execute(
"""
DELETE FROM offline_queue
WHERE id=?
""",
(message_id,)
)


conn.commit()

conn.close()




# ------------------------------------
# Show local history
# ------------------------------------

def show_history():


conn = sqlite3.connect(
DATABASE
)


cursor = conn.cursor()


cursor.execute(
"""
SELECT sender,message,timestamp
FROM messages
"""
)


rows = cursor.fetchall()


conn.close()



print("\n------ LOCAL CHAT HISTORY ------")


for row in rows:

print(
f"{row[2]} | {row[0]}: {row[1]}"
)


print("--------------------------------\n")
