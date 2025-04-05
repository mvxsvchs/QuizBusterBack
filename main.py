from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from Microservice.game_service import random_category_list, random_question_list
from Microservice.user_service import User, register

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React-Frontend (Vite)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register")
async def signup(user: User):
    return register(user)

@app.get("/category")
async def get_category():
    return random_category_list(2)

@app.get("/question")
async def get_question(category:int):
    return random_question_list(category, 3)