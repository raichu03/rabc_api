import os
from dotenv import load_dotenv
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from models import TokenData, Data

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Decodes the JWT and returns user data."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception
    return token_data

def has_permission(required_roles: List[str]):
    def check_roles(current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough privileges to perform this action."
            )
        return True
    return check_roles

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

@router.get("/data")
def read_data(
    current_user: TokenData = Depends(get_current_user),
    _: bool = Depends(has_permission(["admin", "moderator", "viewer"]))
):
    """
    Allows all users to read the data.
    """
    
    return {"message": f"Hello, {current_user.username}! You can view the data."}

@router.post("/data")
def create_data(
    data: Data,
    current_user: TokenData = Depends(get_current_user),
    _: bool = Depends(has_permission(["admin", "moderator"]))
):
    """
    Allows admins and moderators to create new data.
    """
    
    return {"message": f"Data created: '{data.messsage}' by {current_user.username}"}

@router.delete("/data")
def delete_data(
    current_user: TokenData = Depends(get_current_user),
    _: bool = Depends(has_permission(["admin"]))
):
    """
    Allows only admins to delete saved data.
    """
    
    return {"message": f"Data deleted successfully by {current_user.username}."}