"""
mobile_client.py

Mobile chat client.

Features:
- Connects to FastAPI WebSocket backend
- Sends and receives messages
- Saves offline messages when server is unavailable
- Syncs offline messages when connection returns
"""

import asyncio
import json
import websockets


from local_storage import (
    init_storage,
    save_offline_message,
    get_offline_messages,
    remove_offline_message,
    show_history
)


username = ""

server = "ws://127.0.0.1:8000/ws/"

socket = None



# ------------------------------------
# Connect to backend server
# ------------------------------------

async def connect_server():

    global socket

    socket = await websockets.connect(
        server + username
    )

    print("🟢 Connected to server")


    await sync_offline_messages()



# ------------------------------------
# Sync offline messages
# ------------------------------------

async def sync_offline_messages():

    messages = get_offline_messages()


    for msg in messages:

        payload = {

            "type": "message",

            "receiver": msg[1],

            "message": msg[2]

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

        data = json.loads(message)


        if data.get("type") == "message":

            print(
                "\n📩",
                data["sender"],
                ":",
                data["message"]
            )



# ------------------------------------
# Send messages
# ------------------------------------

async def send_messages():

    while True:

        text = await asyncio.to_thread(
            input,
            "\nMessage: "
        )


        if text.lower() == "history":

            show_history()

            continue


        receiver = await asyncio.to_thread(
            input,
            "Send to: "
        )


        payload = {

            "type": "message",

            "receiver": receiver,

            "message": text

        }


        try:

            await socket.send(
                json.dumps(payload)
            )


            print(
                "☁️ Message saved on server"
            )


        except Exception:


            save_offline_message(
                receiver,
                text
            )


            print(
                "📴 Server unavailable. Saved offline"
            )



# ------------------------------------
# Main application
# ------------------------------------

async def main():

    global username


    init_storage()


    print(
        "📱 Local phone storage ready"
    )


    username = input(
        "Username: "
    )


    try:

        await connect_server()


        await asyncio.gather(

            receive_messages(),

            send_messages()

        )


    except Exception as error:


        print(
            "No internet. Offline mode"
        )

        print(
            "Reason:",
            error
        )


        while True:

            text = await asyncio.to_thread(
                input,
                "\nMessage: "
            )


            if text.lower() == "history":

                show_history()

                continue


            receiver = await asyncio.to_thread(
                input,
                "Send to: "
            )


            save_offline_message(
                receiver,
                text
            )


            print(
                "📴 Saved locally"
            )



    finally:

        show_history()



if __name__ == "__main__":

    asyncio.run(main())
