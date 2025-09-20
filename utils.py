from typing import Dict
import json
import os
from dotenv import load_dotenv

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt

from models import UserDB

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_users_db() -> Dict[str, UserDB]:
    """
    Loads users from the JSON file.
    """
    try:
        with open("user.json", "r") as f:
            user_list = json.load(f)
            user_db = {user['username']: user for user in user_list}
            return user_db
    except FileNotFoundError:
        return {}

def verify_password(plain_passowrd: str, hashed_passwored: str) -> bool:
    """
    Checks if a password matches a hashed one.
    """

    return pwd_context.verify(plain_passowrd, hashed_passwored)

def create_access_token(data: dict, expires_delta: float) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(db: dict, username: str) -> dict | None:
    """Retrieves a user from the in-memory database."""
    if username in db:
        return db[username]
    return None

