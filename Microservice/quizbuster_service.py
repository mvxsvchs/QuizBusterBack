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

class Question(BaseModel):
    category: str
    question: str
    correct_answer: str
    incorrect_answers: str[str]

@app.post("/questions")
async def questions(question: Question):
    insert_question(question)
    return

@app.get("/questions")
async def questions():
    return