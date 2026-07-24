"""
websocket_manager.py

Real-time WebSocket connection manager
for Mobile Chat App.

Handles:
- User connections
- Private messages
- Typing status
- Message receipts
- WebRTC audio/video call signaling
"""


from fastapi import WebSocket
from typing import Dict
import json



class ConnectionManager:


    def __init__(self):

        # Stores:
        # username -> websocket connection

        self.active_connections: Dict[str, WebSocket] = {}




    # --------------------------------
    # Connect user
    # --------------------------------

    async def connect(
        self,
        username: str,
        websocket: WebSocket
    ):

        await websocket.accept()


        self.active_connections[username] = websocket


        print(
            f"🟢 {username} connected"
        )


        await self.broadcast_status(
            username,
            "online"
        )





    # --------------------------------
    # Disconnect user
    # --------------------------------

    async def disconnect(
        self,
        username: str
    ):


        if username in self.active_connections:


            del self.active_connections[username]


            print(
                f"🔴 {username} disconnected"
            )


            await self.broadcast_status(
                username,
                "offline"
            )





    # --------------------------------
    # Send private data
    # --------------------------------

    async def send_private_message(
        self,
        receiver,
        data
    ):


        websocket = self.active_connections.get(
            receiver
        )


        if websocket:


            await websocket.send_text(
                json.dumps(data)
            )


            return True



        return False





    # --------------------------------
    # WebRTC Call Signaling
    # --------------------------------

    async def send_call_signal(
        self,
        receiver,
        data
    ):


        websocket = self.active_connections.get(
            receiver
        )


        if websocket:


            await websocket.send_text(
                json.dumps(data)
            )


            return True



        return False





    # --------------------------------
    # Broadcast online status
    # --------------------------------

    async def broadcast_status(
        self,
        username,
        status
    ):


        message = {


            "type":"status",

            "username":username,

            "status":status


        }



        for websocket in list(
            self.active_connections.values()
        ):


            try:


                await websocket.send_text(
                    json.dumps(message)
                )


            except Exception:


                pass





    # --------------------------------
    # Typing indicator
    # --------------------------------

    async def send_typing_status(
        self,
        receiver,
        sender,
        typing
    ):


        data = {


            "type":"typing",

            "sender":sender,

            "typing":typing


        }



        await self.send_private_message(
            receiver,
            data
        )






    # --------------------------------
    # Delivery receipt
    # --------------------------------

    async def send_delivery_receipt(
        self,
        receiver,
        message_id
    ):


        data = {


            "type":"delivered",

            "message_id":message_id


        }



        await self.send_private_message(
            receiver,
            data
        )







    # --------------------------------
    # Read receipt
    # --------------------------------

    async def send_read_receipt(
        self,
        receiver,
        message_id
    ):


        data = {


            "type":"read",

            "message_id":message_id


        }



        await self.send_private_message(
            receiver,
            data
        )






    # --------------------------------
    # Online users
    # --------------------------------

    def online_users(self):


        return list(
            self.active_connections.keys()
        )





# Global manager object

manager = ConnectionManager()
