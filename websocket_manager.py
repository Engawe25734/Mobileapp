"""
websocket_manager.py

Real-time WebSocket Manager
Mobile Chat Application

Handles:
- Multiple user connections
- Private messaging
- Online status
- Typing indicators
- Message receipts
- WebRTC signaling
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



    # =====================================
    # CONNECT USER
    # =====================================


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



    # =====================================
    # DISCONNECT USER
    # =====================================


    async def disconnect(

        self,

        username: str,

        websocket: WebSocket

    ):


        if username not in self.active_connections:

            return



        self.active_connections[username].discard(

            websocket

        )



        if len(self.active_connections[username]) == 0:


            del self.active_connections[username]



            await self.remove_user_from_rooms(

                username

            )



            await self.broadcast_status(

                username,

                "offline"

            )



    # =====================================
    # SEND PRIVATE MESSAGE
    # =====================================


    async def send_private_message(

        self,

        receiver: str,

        data: dict

    ):


        connections = self.active_connections.get(

            receiver,

            set()

        )



        for websocket in list(connections):


            try:


                await websocket.send_text(

                    json.dumps(data)

                )


            except Exception:


                pass



        return len(connections) > 0



    # =====================================
    # BROADCAST USER STATUS
    # =====================================


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



    # =====================================
    # TYPING INDICATOR
    # =====================================


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



    # =====================================
    # DELIVERY RECEIPT
    # =====================================


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



    # =====================================
    # READ RECEIPT
    # =====================================


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



    # =====================================
    # GROUP CALL ROOMS
    # =====================================


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



    async def remove_user_from_rooms(

        self,

        username

    ):


        empty_rooms = []



        for room, users in self.call_rooms.items():


            users.discard(

                username

            )



            if len(users) == 0:


                empty_rooms.append(room)



        for room in empty_rooms:


            del self.call_rooms[room]



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

            "sender":sender,

            "room":room


        }



        for user in users:


            if user != sender:


                await self.send_private_message(

                    user,

                    message

                )



    # =====================================
    # ONLINE USERS
    # =====================================


    def online_users(self):


        return list(

            self.active_connections.keys()

        )



    # =====================================
    # ROOM USERS
    # =====================================


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



# Global instance

manager = ConnectionManager()
