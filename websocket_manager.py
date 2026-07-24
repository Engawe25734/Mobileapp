"""
websocket_manager.py

Real-time WebSocket manager
for Mobile Chat App.

Supports:
- Private messaging
- Multiple device connections
- Online status
- Typing indicator
- Read receipts
- WebRTC audio/video calls
- Group call rooms
"""


from fastapi import WebSocket

from typing import Dict, Set

import json





class ConnectionManager:


    def __init__(self):

        # username -> multiple websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}


        # room_id -> usernames
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



        if username not in self.active_connections:

            self.active_connections[username] = set()



        self.active_connections[username].add(
            websocket
        )



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
        username,
        websocket=None
    ):


        if username not in self.active_connections:

            return



        if websocket:


            self.active_connections[username].discard(
                websocket
            )



        if len(self.active_connections[username]) == 0:


            del self.active_connections[username]



            await self.remove_from_all_rooms(
                username
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


        connections = self.active_connections.get(
            receiver,
            set()
        )



        sent = False



        for websocket in list(connections):

            try:

                await websocket.send_text(
                    json.dumps(data)
                )


                sent = True


            except Exception:


                connections.discard(
                    websocket
                )



        return sent






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



        # maximum participants
        if len(self.call_rooms[room]) >= 10:


            return False



        self.call_rooms[room].add(
            username
        )



        print(
            f"📞 {username} joined room {room}"
        )


        return True






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



        print(
            f"❌ {username} left room {room}"
        )







    # =================================
    # REMOVE USER FROM ALL ROOMS
    # =================================

    async def remove_from_all_rooms(
        self,
        username
    ):


        empty_rooms = []



        for room, users in self.call_rooms.items():


            users.discard(
                username
            )



            if len(users) == 0:


                empty_rooms.append(
                    room
                )



        for room in empty_rooms:


            del self.call_rooms[room]







    # =================================
    # BROADCAST GROUP CALL SIGNAL
    # =================================

    async def broadcast_call_signal(
        self,
        room,
        sender,
        data
    ):


        users = self.call_rooms.get(
            room,
            set()
        )



        message = {


            **data,


            "sender": sender,


            "room": room


        }





        for user in users:


            if user == sender:

                continue



            await self.send_private_message(

                user,

                message

            )







    # =================================
    # ONLINE STATUS
    # =================================

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





        for connections in self.active_connections.values():


            for websocket in list(connections):


                try:


                    await websocket.send_text(

                        json.dumps(message)

                    )


                except Exception:


                    pass







    # =================================
    # TYPING STATUS
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
    # GET ROOM USERS
    # =================================

    def get_room_users(
        self,
        room
    ):


        return list(

            self.call_rooms.get(

                room,

                set()

            )

        )






# GLOBAL INSTANCE

manager = ConnectionManager()
