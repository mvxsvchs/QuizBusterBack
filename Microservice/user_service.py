from fastapi import HTTPException
from pydantic import BaseModel

from Database.user_operations import insert_user, user_exists


class User(BaseModel):
    username: str
    password: str


def register(user: User):
    # Check: Gibt es den User schon?
    if user_exists(user.username):
        raise HTTPException(status_code=404, detail="Benutzername bereits vergeben")

    # Wenn nicht: Speichern
    insert_user(user.username, user.password, "user")
    return {"message": f"{user.username} erstellt"}
