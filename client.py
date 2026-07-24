"""
mobile_client.py

Offline style client.
"""


import asyncio
import json
import websockets


from local_storage import (
init_storage,
save_message,
save_offline_message,
get_offline_messages,
remove_offline_message,
show_history
)



username = ""

server = "ws://127.0.0.1:8000/ws/"

socket = None



# ------------------------------------
# Connect server
# ------------------------------------

async def connect_server():


global socket


socket = await websockets.connect(

server + username

)


print(
"🟢 Connected to server"
)



await sync_offline_messages()



# ------------------------------------
# Send queued messages
# ------------------------------------

async def sync_offline_messages():


messages = get_offline_messages()


for msg in messages:


payload = {


"type":"message",


"receiver":msg[1],


"message":msg[2]

}



await socket.send(

json.dumps(payload)

)


remove_offline_message(

msg[0]

)



if messages:

print(
"☁️ Offline messages synced"
)




# ------------------------------------
# Receive messages
# ------------------------------------

async def receive_messages():


async for message in socket:


data=json.loads(message)


if data["type"]=="message":


print(

"\n📩",

data["sender"],

":",

data["message"]

)



save_message(

data["sender"],

username,

data["message"]

)





# ------------------------------------
# Send message
# ------------------------------------

async def send_messages():


while True:


text = await asyncio.to_thread(

input,

"Message: "

)



if text=="history":

show_history()

continue




receiver=input(

"Send to: "

)



payload={

"type":"message",

"receiver":receiver,

"message":text

}



try:


await socket.send(

json.dumps(payload)

)


save_message(

username,

receiver,

text

)



except:


save_offline_message(

receiver,

text

)



print(

"📴 Saved offline"

)





# ------------------------------------
# Start application
# ------------------------------------

async def main():


global username


init_storage()



username=input(

"Username: "

)



try:


await connect_server()



await asyncio.gather(

receive_messages(),

send_messages()

)



except Exception:


print(

"No internet. Offline mode"

)


show_history()





if __name__=="__main__":


asyncio.run(main())
