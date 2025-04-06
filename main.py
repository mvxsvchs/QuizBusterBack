from typing import Annotated

import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from starlette.middleware.cors import CORSMiddleware

from Config.JWT_config import SECRET_KEY, ALGORITHM
from Microservice.achievement_service import user_achievements, all_achievements, add_user_achievement, Achievement
from Microservice.game_service import random_category_list, random_question_list
from Microservice.user_service import User, register, login, get_user, Score, update_score, get_leaderboard

# API Service wird erstellt
app = FastAPI()
# API Service config für die Website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],  # React-Frontend (Vite)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Das Schema für die Token Verifizierung wird festgelegt
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Der gegebene Token wird überprüft
async def verify_user_token(token: Annotated[str, Depends(oauth2_scheme)]):
    # Definition der Exception die gegeben wird, wenn ein Fehler auftritt
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Der Token wird dekodiert anhand der JWT config
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Der Nutzername wird aus dem Token entnommen
        username = payload.get("sub")
        # Wenn der Token keinen Nutzernamen enthält
        if username is None:
            # Gib die Exception zurück
            raise credentials_exception
    # Wenn der gegebene Token nicht valide ist
    except InvalidTokenError:
        # Gib die Exception zurück
        raise credentials_exception
    # Nutzer wird aus Datenbank abgefragt
    user = get_user(username=username)
    # Wenn Nutzer nicht existiert
    if user is None:
        # Gib die Exception zurück
        raise credentials_exception
    # Gib das gefundene Nutzer-Objekt zurück
    return user


@app.post("/register")
async def post_signup(user: User):
    return register(user)


@app.post("/token")
# In der Request werden die Login-Daten des Nutzers gefordert
async def post_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return login(form_data)


@app.patch("/user/score")
# In der Request wird ein Nutzertoken gefordert und mit der verify_user_token Funktion verifiziert
async def patch_score(current_user: Annotated[User, Depends(verify_user_token)], score: Score):
    return update_score(current_user.username, score)


@app.get("/category")
async def get_category():
    return random_category_list(2)


@app.get("/question")
async def get_question(category: int):
    return random_question_list(category, 3)


@app.get("/score")
async def get_scores():
    return get_leaderboard(10)


@app.get("/achievement")
async def get_achievements():
    return all_achievements()


@app.get("/user/achievement")
# In der Request wird ein Nutzertoken gefordert und mit der verify_user_token Funktion verifiziert
async def get_user_achievements(current_user: Annotated[User, Depends(verify_user_token)]):
    return user_achievements()


@app.patch("/user/achievement")
# In der Request wird ein Nutzertoken gefordert und mit der verify_user_token Funktion verifiziert
async def patch_user_achievement(current_user: Annotated[User, Depends(verify_user_token)], achievement: Achievement):
    return add_user_achievement()
