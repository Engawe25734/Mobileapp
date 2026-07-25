"""
file_manager.py

chatMe File Manager

Features:
- Image upload
- Video upload
- Audio upload
- Document upload
- File validation
- Attachment storage
- File information

Used by:
- server.py
- message_manager.py
"""


import os
import uuid
import datetime



UPLOAD_FOLDER = "uploads"



MAX_FILE_SIZE = 100 * 1024 * 1024   # 100 MB




ALLOWED_TYPES = {

    # Images
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",


    # Video
    "video/mp4",
    "video/webm",
    "video/quicktime",


    # Audio
    "audio/mpeg",
    "audio/wav",
    "audio/ogg",


    # Documents
    "application/pdf",
    "application/msword",
    "text/plain"

}





# =====================================
# CREATE UPLOAD FOLDER
# =====================================


def initialize_storage():


    if not os.path.exists(UPLOAD_FOLDER):

        os.makedirs(

            UPLOAD_FOLDER

        )






# =====================================
# VALIDATE FILE
# =====================================


def validate_file(

    filename,

    content_type,

    size

):


    if content_type not in ALLOWED_TYPES:


        return False, "File type not supported"




    if size > MAX_FILE_SIZE:


        return False, "File too large"




    return True, "Allowed"






# =====================================
# SAVE FILE
# =====================================


def save_file(

    file_data,

    filename

):


    initialize_storage()



    extension = os.path.splitext(

        filename

    )[1]



    new_name = (

        str(uuid.uuid4())

        +

        extension

    )



    path = os.path.join(

        UPLOAD_FOLDER,

        new_name

    )



    with open(

        path,

        "wb"

    ) as f:


        f.write(

            file_data

        )



    return {


        "filename":filename,


        "stored_name":new_name,


        "path":path,


        "uploaded":

        str(datetime.datetime.now())

    }







# =====================================
# FILE CATEGORY
# =====================================


def get_file_category(

    content_type

):


    if content_type.startswith(

        "image"

    ):

        return "image"



    if content_type.startswith(

        "video"

    ):

        return "video"



    if content_type.startswith(

        "audio"

    ):

        return "audio"



    return "document"







# =====================================
# DELETE FILE
# =====================================


def delete_file(

    path

):


    if os.path.exists(path):


        os.remove(path)


        return True



    return False






# =====================================
# FILE DETAILS
# =====================================


def file_information(

    filename,

    content_type,

    size

):


    return {


        "name":filename,


        "type":content_type,


        "category":

        get_file_category(

            content_type

        ),


        "size":size,


        "uploaded":

        str(datetime.datetime.now())

    }






# =====================================
# TEST
# =====================================


if __name__=="__main__":


    initialize_storage()



    print(

        "✅ chatMe File Manager Ready"

    )
