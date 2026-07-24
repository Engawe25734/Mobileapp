"""
mobile_client.py

Mobile chat client.

Features:
- FastAPI WebSocket connection
- Backend message saving
- Offline message queue
- Offline sync
- Local history display
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


        await asyncio.sleep(0.2)


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


            # store local copy
            save_message(

                data["sender"],

                username,

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

                "☁️ Sent to server"

            )



        except Exception:


            save_offline_message(

                receiver,

                text

            )


            print(

                "📴 Saved offline"

            )



# ------------------------------------
# Main
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
