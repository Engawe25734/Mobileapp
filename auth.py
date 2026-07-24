"""
auth.py

Authentication system for WhatsApp Clone.

Features:
- Secure password hashing
- User registration
- User login
- JWT authentication
"""


from datetime import datetime, timedelta

from passlib.context import CryptContext

from jose import jwt, JWTError

from database import (
create_user,
get_user_by_phone
)



# ------------------------------------
# Security configuration
# ------------------------------------


SECRET_KEY = "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY"

ALGORITHM = "HS256"

TOKEN_EXPIRE_MINUTES = 60



# Password encryption engine

password_context = CryptContext(
schemes=["bcrypt"],
deprecated="auto"
)



# ------------------------------------
# Password functions
# ------------------------------------


def hash_password(password: str):

"""
Converts plain password into encrypted hash
"""

return password_context.hash(password)




def verify_password(
plain_password,
hashed_password
):

"""
Checks if password matches stored hash
"""

return password_context.verify(
plain_password,
hashed_password
)



# ------------------------------------
# User registration
# ------------------------------------


def register_user(
username,
phone,
password
):


# Check existing user

existing_user = get_user_by_phone(phone)


if existing_user:

return {
"status": "error",
"message": "Phone number already registered"
}



password_hash = hash_password(password)



user_id = create_user(
username,
phone,
password_hash
)


return {

"status": "success",

"message": "Account created",

"user_id": user_id

}




# ------------------------------------
# User login
# ------------------------------------


def authenticate_user(
phone,
password
):


user = get_user_by_phone(phone)



if not user:

return None



if not verify_password(
password,
user["password_hash"]
):

return None



return user



# ------------------------------------
# JWT creation
# ------------------------------------


def create_access_token(
user_id,
username
):


expiration = datetime.utcnow() + timedelta(
minutes=TOKEN_EXPIRE_MINUTES
)


payload = {

"user_id": user_id,

"username": username,

"exp": expiration

}


token = jwt.encode(

payload,

SECRET_KEY,

algorithm=ALGORITHM

)


return token




# ------------------------------------
# JWT verification
# ------------------------------------


def verify_token(token):


try:

payload = jwt.decode(

token,

SECRET_KEY,

algorithms=[ALGORITHM]

)


return payload



except JWTError:


return None




# ------------------------------------
# Test authentication
# ------------------------------------


if __name__ == "__main__":


from database import initialize_database


initialize_database()


print("\n--- Creating Test User ---")


result = register_user(

"Alex",

"5551234567",

"password123"

)


print(result)



print("\n--- Testing Login ---")


user = authenticate_user(

"5551234567",

"password123"

)


if user:


token = create_access_token(

user["id"],

user["username"]

)


print("Login successful")

print("JWT Token:")

print(token)


else:

print("Login failed")
