"""
cloud_storage.py

chatMe Cloud Storage Manager

Features:
- Image uploads
- Video uploads
- Audio uploads
- Document uploads
- File validation
- Secure file URLs
- Cloud provider ready

Supported later:
- AWS S3
- Cloudinary
- Google Cloud Storage

Used by:
- server.py
- app.js
"""


import os
import uuid
import mimetypes
from datetime import datetime



# =====================================
# STORAGE CONFIGURATION
# =====================================


STORAGE_FOLDER = "uploads"



MAX_FILE_SIZE = 100 * 1024 * 1024
# 100MB



ALLOWED_TYPES = [

    "image",

    "video",

    "audio",

    "application/pdf",

    "text"

]




# Create upload folder

os.makedirs(

    STORAGE_FOLDER,

    exist_ok=True

)





# =====================================
# CHECK FILE TYPE
# =====================================


def allowed_file(

    content_type

):


    """
    Validate uploaded file type
    """



    if not content_type:

        return False



    for item in ALLOWED_TYPES:


        if content_type.startswith(item):


            return True



    return False






# =====================================
# SAVE FILE
# =====================================


def upload_file(

    file,

    username

):


    """
    Save uploaded file

    Returns:
        file information
    """



    if not allowed_file(

        file.content_type

    ):


        raise ValueError(

            "File type not supported"

        )




    filename = (

        str(uuid.uuid4())

        +

        "_"

        +

        file.filename

    )



    filepath = os.path.join(

        STORAGE_FOLDER,

        filename

    )





    content = file.file.read()



    if len(content) > MAX_FILE_SIZE:


        raise ValueError(

            "File exceeds maximum size"

        )





    with open(

        filepath,

        "wb"

    ) as output:


        output.write(

            content

        )





    return {


        "filename":file.filename,


        "stored_name":filename,


        "path":filepath,


        "url":

        "/uploads/" + filename,


        "type":file.content_type,


        "owner":username,


        "uploaded":

        str(datetime.now())


    }







# =====================================
# DELETE FILE
# =====================================


def delete_file(

    filepath

):


    """
    Delete uploaded file
    """



    if os.path.exists(filepath):


        os.remove(filepath)


        return True



    return False





# =====================================
# FILE INFORMATION
# =====================================


def get_file_info(

    filepath

):


    """
    Return file metadata
    """



    if not os.path.exists(filepath):


        return None




    size = os.path.getsize(

        filepath

    )



    file_type = mimetypes.guess_type(

        filepath

    )[0]




    return {


        "path":filepath,


        "size":size,


        "type":file_type


    }





# =====================================
# DOWNLOAD URL
# =====================================


def generate_download_url(

    filename

):


    """
    Generate public download path

    Replace later with:
    AWS signed URL
    Cloudinary URL
    """



    return (

        "/uploads/"

        +

        filename

    )







# =====================================
# CLOUD PROVIDER PLACEHOLDER
# =====================================


def upload_to_cloud(

    filepath

):


    """
    Cloud integration point


    Example:

    AWS S3:

        boto3.client("s3")


    Cloudinary:

        cloudinary.uploader.upload()

    """



    print(

        "Cloud upload pending:",

        filepath

    )



    return {


        "success":True,


        "url":

        generate_download_url(

            os.path.basename(filepath)

        )


    }






# =====================================
# TEST
# =====================================


if __name__ == "__main__":


    print(

        "chatMe Cloud Storage Ready"

    )
