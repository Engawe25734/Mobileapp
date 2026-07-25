"""
notification_manager.py

chatMe Notification Manager

Features:
- Message alerts
- Call alerts
- Friend request alerts
- Notification history
- Read/unread status
- Notification counter

Used by:
- server.py
- websocket_manager.py
- message_manager.py
"""


import datetime


from database_manager import get_connection





# =====================================
# CREATE NOTIFICATION
# =====================================


def create_notification(

    receiver,

    sender,

    title,

    message,

    notification_type="message"

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

    """

    INSERT INTO notifications

    (

    receiver,

    sender,

    title,

    message,

    type,

    is_read,

    created

    )

    VALUES(?,?,?,?,?,?,?)

    """,

    (

        receiver,

        sender,

        title,

        message,

        notification_type,

        0,

        str(datetime.datetime.now())

    )

    )



    conn.commit()

    conn.close()



    return True






# =====================================
# GET USER NOTIFICATIONS
# =====================================


def get_notifications(

    username

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

    """

    SELECT *

    FROM notifications

    WHERE receiver=?

    ORDER BY id DESC

    """,

    (

        username,

    )

    )



    notifications = cursor.fetchall()



    conn.close()



    result=[]



    for item in notifications:


        result.append(

        {


            "id":item[0],


            "receiver":item[1],


            "sender":item[2],


            "title":item[3],


            "message":item[4],


            "type":item[5],


            "read":bool(item[6]),


            "created":item[7]


        }

        )


    return result






# =====================================
# UNREAD COUNT
# =====================================


def unread_count(

    username

):


    conn=get_connection()

    cursor=conn.cursor()



    cursor.execute(

    """

    SELECT COUNT(*)

    FROM notifications

    WHERE receiver=?

    AND is_read=0

    """,

    (

        username,

    )

    )



    count=cursor.fetchone()[0]



    conn.close()



    return count






# =====================================
# MARK AS READ
# =====================================


def mark_read(

    notification_id

):


    conn=get_connection()

    cursor=conn.cursor()



    cursor.execute(

    """

    UPDATE notifications

    SET is_read=1

    WHERE id=?

    """,

    (

        notification_id,

    )

    )



    conn.commit()

    conn.close()



    return True






# =====================================
# MARK ALL READ
# =====================================


def mark_all_read(

    username

):


    conn=get_connection()

    cursor=conn.cursor()



    cursor.execute(

    """

    UPDATE notifications

    SET is_read=1

    WHERE receiver=?

    """,

    (

        username,

    )

    )



    conn.commit()

    conn.close()



    return True






# =====================================
# DELETE NOTIFICATION
# =====================================


def delete_notification(

    notification_id

):


    conn=get_connection()

    cursor=conn.cursor()



    cursor.execute(

    """

    DELETE FROM notifications

    WHERE id=?

    """,

    (

        notification_id,

    )

    )



    conn.commit()

    conn.close()



    return True






# =====================================
# CLEAR USER NOTIFICATIONS
# =====================================


def clear_notifications(

    username

):


    conn=get_connection()

    cursor=conn.cursor()



    cursor.execute(

    """

    DELETE FROM notifications

    WHERE receiver=?

    """,

    (

        username,

    )

    )



    conn.commit()

    conn.close()



    return True






# =====================================
# MESSAGE ALERT
# =====================================


def message_notification(

    sender,

    receiver,

    message

):


    return create_notification(

        receiver,

        sender,

        "New Message",

        message,

        "message"

    )






# =====================================
# CALL ALERT
# =====================================


def call_notification(

    caller,

    receiver,

    call_type

):


    return create_notification(

        receiver,

        caller,

        "Incoming Call",

        f"{call_type} call from {caller}",

        "call"

    )






# =====================================
# FRIEND REQUEST ALERT
# =====================================


def friend_request_notification(

    sender,

    receiver

):


    return create_notification(

        receiver,

        sender,

        "Friend Request",

        f"{sender} sent you a friend request",

        "friend"

    )






# =====================================
# TEST
# =====================================


if __name__=="__main__":


    print(

        "✅ chatMe Notification Manager Ready"

    )
