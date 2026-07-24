"""
websocket_manager.py

Real-Time WebSocket Manager
Mobile Chat App Backend

Supports:
- Multiple users
- Multiple devices per user
- Private messages
- Online status
- Typing indicators
- Read receipts
- WebRTC signaling
- Group audio/video call rooms
"""


from fastapi import WebSocket

from typing import Dict, Set

import json






class ConnectionManager:


    def __init__(self):


        # username -> multiple websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}


        # call_room -> usernames
        self.call_rooms: Dict[str, Set[str]] = {}







    # ======================================
    # CONNECT USER
    # ======================================


    async def connect(
        self,
        username: str,
        websocket: WebSocket
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







    # ======================================
    # DISCONNECT USER
    # ======================================


    async def disconnect(
        self,
        username: str,
        websocket: WebSocket
    ):


        if username in self.active_connections:


            self.active_connections[username].discard(
                websocket
            )



            # Remove user completely
            # when no devices remain

            if len(self.active_connections[username]) == 0:


                del self.active_connections[username]



                await self.remove_from_all_rooms(
                    username
                )



                await self.broadcast_status(
                    username,
                    "offline"
                )







    # ======================================
    # SEND MESSAGE TO USER
    # ======================================


    async def send_private_message(
        self,
        username: str,
        data: dict
    ):


        connections = self.active_connections.get(
            username,
            set()
        )



        for websocket in connections:


            try:


                await websocket.send_text(

                    json.dumps(data)

                )


            except Exception:


                pass







    # ======================================
    # ONLINE STATUS
    # ======================================


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


            for websocket in connections:


                try:


                    await websocket.send_text(

                        json.dumps(message)

                    )


                except Exception:


                    pass







    # ======================================
    # TYPING INDICATOR
    # ======================================


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








    # ======================================
    # READ RECEIPTS
    # ======================================


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







    # ======================================
    # CREATE GROUP CALL ROOM
    # ======================================


    async def create_room(
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
            f"📞 {username} created room {room}"
        )







    # ======================================
    # JOIN GROUP CALL
    # ======================================


    async def join_room(
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
            f"👥 {username} joined {room}"
        )







    # ======================================
    # LEAVE GROUP CALL
    # ======================================


    async def leave_room(
        self,
        room,
        username
    ):


        if room in self.call_rooms:


            self.call_rooms[room].discard(
                username
            )



            if not self.call_rooms[room]:

                del self.call_rooms[room]








    # ======================================
    # REMOVE USER FROM ALL CALLS
    # ======================================


    async def remove_from_all_rooms(
        self,
        username
    ):


        empty=[]



        for room, users in self.call_rooms.items():


            users.discard(
                username
            )



            if len(users)==0:

                empty.append(room)





        for room in empty:

            del self.call_rooms[room]








    # ======================================
    # BROADCAST GROUP CALL SIGNAL
    # ======================================


    async def broadcast_room(
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


            "sender":sender,


            "room":room


        }




        for user in users:


            if user == sender:

                continue



            await self.send_private_message(

                user,

                message

            )








    # ======================================
    # GET ONLINE USERS
    # ======================================


    def online_users(self):


        return list(

            self.active_connections.keys()

        )







    # ======================================
    # GET ROOM MEMBERS
    # ======================================


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







# GLOBAL CONNECTION MANAGER

manager = ConnectionManager()
