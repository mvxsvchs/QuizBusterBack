from fastapi import FastAPI
from pydantic import BaseModel

from Database.user_operations import insert_user

app = FastAPI()


class User(BaseModel): #Register
    username: str
    password: str

@app.post("/register")
async def register(user: User):
    insert_user(user.username, user.password, "user")
    return {"message": f"{user.username} erstellt"}