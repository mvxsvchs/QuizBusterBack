from datetime import datetime, timezone, timedelta
from typing import Annotated

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext

from Config.JWT_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from Database.user_operations import insert_user, user_exists, get_user


# Klasse für das User JSON
class User(BaseModel):
    username: str
    password: str


# Klasse für das Token JSON
class Token(BaseModel):
    access_token: str
    token_type: str


# Kontext zum verschlüsseln des Passworts
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Verschlüsselung des Passworts
def get_password_hash(password):
    return pwd_context.hash(password)


# Vergleich von verschlüsselten Passwörtern
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Überprüfung ob Login Daten korrekt sind
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


# Erstellen von JWT Token zur Authentifizierung
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def register(user: User) -> Token:
    # Check: Gibt es den User schon?
    if user_exists(user.username):
        raise HTTPException(status_code=404, detail="Benutzername bereits vergeben")

    # Wenn nicht: Speichern
    insert_user(user.username, get_password_hash(user.password), "user")
    access_token = create_access_token(data={"sub": user.username})

    return Token(access_token=access_token, token_type="bearer")


def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Falscher Nutzername oder Passwort",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})

    return Token(access_token=access_token, token_type="bearer")
