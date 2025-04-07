# Utils/auth_utils.py

from jwt import decode, InvalidTokenError
from fastapi import HTTPException
from Config.jwt_config import SECRET_KEY, ALGORITHM
from Microservice.user_service import get_user
from Database.user_operations import UserModel

async def verify_user_token(token: str) -> UserModel:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError as e:
        raise credentials_exception from e

    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    return user
