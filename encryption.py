"""
encryption.py

chatMe End-to-End Encryption Module

Features:
- Generate encryption keys
- Encrypt messages before storage/sending
- Decrypt messages after receiving
- Secure message protection

Used by:
- server.py
- websocket_manager.py
- database.py
"""


from cryptography.fernet import Fernet
import os


# =====================================
# KEY MANAGEMENT
# =====================================


KEY_FILE = "secret.key"



def generate_key():

    """
    Create encryption key
    """

    if not os.path.exists(KEY_FILE):

        key = Fernet.generate_key()

        with open(KEY_FILE, "wb") as file:

            file.write(key)


        return key


    else:

        return load_key()





def load_key():

    """
    Load existing encryption key
    """

    with open(KEY_FILE, "rb") as file:

        return file.read()





# Initialize encryption system

ENCRYPTION_KEY = generate_key()


cipher = Fernet(
    ENCRYPTION_KEY
)





# =====================================
# ENCRYPT MESSAGE
# =====================================


def encrypt_message(message:str):

    """
    Encrypt a text message

    Input:
        Plain text

    Output:
        Encrypted text
    """


    if not message:

        return ""



    encrypted = cipher.encrypt(

        message.encode("utf-8")

    )


    return encrypted.decode("utf-8")





# =====================================
# DECRYPT MESSAGE
# =====================================


def decrypt_message(encrypted_message:str):

    """
    Decrypt encrypted message

    Input:
        Encrypted text

    Output:
        Original message
    """



    if not encrypted_message:

        return ""



    try:


        decrypted = cipher.decrypt(

            encrypted_message.encode("utf-8")

        )


        return decrypted.decode("utf-8")



    except Exception:


        return "[Unable to decrypt message]"





# =====================================
# TEST FUNCTION
# =====================================


if __name__ == "__main__":


    message = "Hello from chatMe"


    print(
        "Original:",
        message
    )


    encrypted = encrypt_message(

        message

    )


    print(

        "Encrypted:",

        encrypted

    )



    decrypted = decrypt_message(

        encrypted

    )


    print(

        "Decrypted:",

        decrypted

    )
