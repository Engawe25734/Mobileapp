"""
profile_manager.py

chatMe User Profile Manager

Features:
- Upload profile pictures
- Store avatar paths
- Delete avatars
- Retrieve user avatars
- Image validation

Used by:
- server.py
- database.py
- app.js
"""


import os
import uuid

from PIL import Image



# =====================================
# CONFIGURATION
# =====================================


PROFILE_FOLDER = "profiles"

ALLOWED_EXTENSIONS = [

    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp"

]


DEFAULT_AVATAR = "/static/default-avatar.png"



# Create profile folder

os.makedirs(

    PROFILE_FOLDER,

    exist_ok=True

)




# =====================================
# VALIDATE IMAGE
# =====================================


def validate_image(filename):

    """
    Check if uploaded file is an image
    """


    extension = os.path.splitext(

        filename

    )[1].lower()



    return extension in ALLOWED_EXTENSIONS





# =====================================
# SAVE PROFILE PICTURE
# =====================================


def save_profile_picture(
    file,
    username
):

    """
    Save user avatar

    Parameters:
        file:
            Uploaded image file

        username:
            User account name

    Returns:
        image path
    """



    if not validate_image(

        file.filename

    ):


        raise ValueError(

            "Invalid image format"

        )



    extension = os.path.splitext(

        file.filename

    )[1].lower()



    filename = (

        username

        +

        "_"

        +

        str(uuid.uuid4())

        +

        extension

    )



    filepath = os.path.join(

        PROFILE_FOLDER,

        filename

    )



    # Save file

    with open(

        filepath,

        "wb"

    ) as buffer:


        buffer.write(

            file.file.read()

        )




    # Resize image

    try:


        image = Image.open(

            filepath

        )


        image.thumbnail(

            (500,500)

        )


        image.save(

            filepath

        )


    except Exception:


        pass




    return filepath





# =====================================
# DELETE PROFILE PICTURE
# =====================================


def delete_profile_picture(

    filepath

):

    """
    Remove old avatar
    """



    if filepath and os.path.exists(filepath):


        os.remove(

            filepath

        )


        return True



    return False






# =====================================
# GET PROFILE PICTURE
# =====================================


def get_profile_picture(

    filepath

):


    """
    Return avatar URL

    If no image exists,
    return default avatar
    """



    if filepath and os.path.exists(filepath):


        return (

            "/"

            +

            filepath.replace(

                "\\",

                "/"

            )

        )



    return DEFAULT_AVATAR





# =====================================
# CHANGE PROFILE PICTURE
# =====================================


def change_profile_picture(

    old_picture,

    new_file,

    username

):


    """
    Replace existing avatar
    """



    delete_profile_picture(

        old_picture

    )



    return save_profile_picture(

        new_file,

        username

    )





# =====================================
# TEST
# =====================================


if __name__ == "__main__":


    print(

        "chatMe Profile Manager Ready"

    )
