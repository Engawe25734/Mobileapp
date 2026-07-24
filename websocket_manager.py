"""
websocket_manager.py

Real-time WebSocket manager
for Mobile Chat App.

Supports:
- Private chat
- Online status
- Typing indicator
- Read receipts
- Audio/video call signaling
- Group call rooms
"""


from fastapi import WebSocket

from typing import Dict, Set

import json





class ConnectionManager:


    def __init__(self):

        # username -> websocket

        self.active_connections: Dict[str, WebSocket] = {}


        # room -> usernames

        self.call_rooms: Dict[str, Set[str]] = {}






    # =================================
    # CONNECT USER
    # =================================


    async def connect(
        self,
        username,
        websocket
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






    # =================================
    # DISCONNECT USER
    # =================================


    async def disconnect(
        self,
        username
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






    # =================================
    # PRIVATE MESSAGE
    # =================================


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







    # =================================
    # CALL SIGNAL PRIVATE
    # =================================


    async def send_call_signal(
        self,
        receiver,
        data
    ):


        return await self.send_private_message(
            receiver,
            data
        )








    # =================================
    # JOIN GROUP CALL ROOM
    # =================================


    async def join_call_room(
        self,
        room,
        username
    ):


        if room not in self.call_rooms:

            self.call_rooms[room] = set()



        self.call_rooms[room].add(
            username
        )


        print(
            username,
            "joined",
            room
        )








    # =================================
    # LEAVE GROUP CALL ROOM
    # =================================


    async def leave_call_room(
        self,
        room,
        username
    ):


        if room in self.call_rooms:


            self.call_rooms[room].discard(
                username
            )


            if len(self.call_rooms[room]) == 0:

                del self.call_rooms[room]







    # =================================
    # BROADCAST CALL SIGNAL
    # =================================


    async def broadcast_call_signal(
        self,
        room,
        sender,
        data
    ):


        if room not in self.call_rooms:

            return



        message = {

            **data,

            "sender":sender,

            "room":room

        }




        for user in self.call_rooms[room]:


            if user == sender:

                continue



            websocket = self.active_connections.get(
                user
            )



            if websocket:


                try:

                    await websocket.send_text(
                        json.dumps(message)
                    )


                except Exception:

                    pass







    # =================================
    # ONLINE STATUS
    # =================================


    async def broadcast_status(
        self,
        username,
        status
    ):



        message={

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








    # =================================
    # TYPING
    # =================================


    async def send_typing_status(
        self,
        receiver,
        sender,
        typing
    ):


        await self.send_private_message(

            receiver,

            {

            "type":"typing",

            "sender":sender,

            "typing":typing

            }

        )







    # =================================
    # DELIVERY RECEIPT
    # =================================


    async def send_delivery_receipt(
        self,
        receiver,
        message_id
    ):


        await self.send_private_message(

            receiver,

            {

            "type":"delivered",

            "message_id":message_id

            }

        )







    # =================================
    # READ RECEIPT
    # =================================


    async def send_read_receipt(
        self,
        receiver,
        message_id
    ):


        await self.send_private_message(

            receiver,

            {

            "type":"read",

            "message_id":message_id

            }

        )







    # =================================
    # ONLINE USERS
    # =================================


    def online_users(self):


        return list(
            self.active_connections.keys()
        )







    # =================================
    # CALL ROOM USERS
    # =================================


    def get_room_users(
        self,
        room
    ):


        return list(
            self.call_rooms.get(
                room,
                []
            )
        )







# GLOBAL OBJECT

manager = ConnectionManager()
