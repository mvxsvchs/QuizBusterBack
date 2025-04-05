from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from Database.user_operations import insert_user, user_exists


app = FastAPI()
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from Database.user_operations import insert_user, user_exists

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React-Frontend (Vite)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    username: str
    password: str

@app.post("/register")
async def register(user: User):
    # Check: Gibt es den User schon?
    if user_exists(user.username):
        raise HTTPException(status_code=404, detail="Benutzername bereits vergeben")

    # Wenn nicht: Speichern
    insert_user(user.username, user.password, "user")
    return {"message": f"{user.username} erstellt"}

