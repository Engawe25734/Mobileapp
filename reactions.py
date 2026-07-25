"""
reactions.py

chatMe Message Reaction Manager

Features:
- Add reactions
- Remove reactions
- Count reactions
- Retrieve reactions

Supported emojis:
❤️ 👍 😂 😮 😢 🔥

Used by:
- server.py
- websocket_manager.py
- database.py
"""


from collections import defaultdict



# =====================================
# AVAILABLE REACTIONS
# =====================================


AVAILABLE_REACTIONS = [

    "❤️",
    "👍",
    "😂",
    "😮",
    "😢",
    "🔥"

]





# =====================================
# TEMPORARY MEMORY STORAGE
# =====================================
#
# Format:
#
# {
#    message_id:{
#        username:"emoji"
#    }
# }
#
# Later this can move into SQLite
#



message_reactions = defaultdict(dict)





# =====================================
# ADD REACTION
# =====================================


def add_reaction(

    message_id,

    username,

    reaction

):


    """
    Add emoji reaction to message
    """



    if reaction not in AVAILABLE_REACTIONS:


        return {


            "success":False,


            "message":"Invalid reaction"

        }





    message_reactions[message_id][username] = reaction



    return {


        "success":True,


        "message_id":message_id,


        "username":username,


        "reaction":reaction


    }





# =====================================
# REMOVE REACTION
# =====================================


def remove_reaction(

    message_id,

    username

):


    """
    Remove user's reaction
    """



    if message_id in message_reactions:


        if username in message_reactions[message_id]:


            del message_reactions[message_id][username]



            return {


                "success":True,


                "message":"Reaction removed"

            }





    return {


        "success":False,


        "message":"Reaction not found"

    }






# =====================================
# GET MESSAGE REACTIONS
# =====================================


def get_reactions(

    message_id

):


    """
    Return all reactions
    for a message
    """



    reactions = message_reactions.get(

        message_id,

        {}

    )



    return reactions






# =====================================
# COUNT REACTIONS
# =====================================


def count_reactions(

    message_id

):


    """
    Count emoji totals
    """



    result = {}



    reactions = message_reactions.get(

        message_id,

        {}

    )



    for emoji in reactions.values():


        if emoji not in result:


            result[emoji] = 0



        result[emoji] += 1



    return result






# =====================================
# USER REACTION
# =====================================


def get_user_reaction(

    message_id,

    username

):


    """
    Check user's reaction
    """



    return message_reactions.get(

        message_id,

        {}

    ).get(

        username

    )






# =====================================
# CLEAR MESSAGE REACTIONS
# =====================================


def delete_message_reactions(

    message_id

):


    """
    Remove all reactions
    when message is deleted
    """



    if message_id in message_reactions:


        del message_reactions[message_id]


        return True



    return False






# =====================================
# TEST
# =====================================


if __name__ == "__main__":


    add_reaction(

        1,

        "elvis",

        "❤️"

    )


    add_reaction(

        1,

        "john",

        "👍"

    )


    print(

        get_reactions(1)

    )


    print(

        count_reactions(1)

    )
