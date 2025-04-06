from typing import Annotated

import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from starlette.middleware.cors import CORSMiddleware

from Config.JWT_config import SECRET_KEY, ALGORITHM
from Microservice.game_service import random_category_list, random_question_list
from Microservice.user_service import User, register, login, get_user, Score, add_score

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],  # React-Frontend (Vite)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_user_token(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    return user


@app.post("/register")
async def signup(user: User):
    return register(user)


@app.post("/token")
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return login(form_data)


@app.patch("/user/score")
async def update_score(current_user: Annotated[User, Depends(verify_user_token)], score: Score):
    return add_score(current_user.username, score)


@app.get("/category")
async def get_category():
    return random_category_list(2)


@app.get("/question")
async def get_question(category: int):
    return random_question_list(category, 3)
