"""Hauptmodul der Quizbuster API Anwendung.

Dieses Modul initialisiert die FastAPI-App, konfiguriert CORS-Middleware
und definiert die API-Endpunkte für verschiedene Funktionalitäten.

Es integriert Logik aus verschiedenen "Microservice"-Modulen
(user_service, game_service, achievement_service) und stellt eine
zentrale Abhängigkeitsfunktion (`verify_user_token`) zur Überprüfung
von JWT-Bearer-Tokens bereit.
"""
from typing import Annotated

import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from starlette.middleware.cors import CORSMiddleware

from Config.jwt_config import SECRET_KEY, ALGORITHM
from Database.user_operations import UserModel
from Microservice.achievement_service import (
    user_achievements,
    all_achievements,
    unlock_user_achievement,
    Achievement,
)
from Microservice.game_service import random_category_list, random_question_list
from Microservice.user_service import (
    User,
    register,
    login,
    get_user,
    Score,
    update_score,
    get_leaderboard, Token,
)

# region ↓ App Initialisierung und Konfiguration ↓

# API Service wird erstellt
app = FastAPI(title="Quiz Game API", version="1.0.0")

# API Service config für die Website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Erlaubt Anfragen vom React-Frontend
    allow_credentials=True,  # Erlaubt Cookies/Credentials
    allow_methods=["*"],  # Erlaubt alle HTTP-Methoden
    allow_headers=["*"],  # Erlaubt alle HTTP-Header
)

# Das Schema für die Token Verifizierung wird festgelegt
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# endregion

# region ↓ Authentifizierung ↓

async def verify_user_token(token: Annotated[str, Depends(oauth2_scheme)]) -> UserModel:
    """Überprüft das übergebene JWT Bearer Token und gibt den zugehörigen Benutzer zurück.

    Diese Funktion wird verwendet, um Endpunkte zu schützen.
    Sie dekodiert das Token, validiert seinen Inhalt
    und prüft, ob der Benutzer in der Datenbank existiert.

    Args:
        token (Annotated[str, Depends(oauth2_scheme)]): Das JWT-Token, das
            automatisch aus dem 'Authorization: Bearer <token>' Header extrahiert wird.

    Raises:
        HTTPException (401 Unauthorized): Wenn das Token ungültig ist (Format, Signatur),
            der 'sub'-Claim fehlt, oder der Benutzer aus dem Token nicht in der
            Datenbank gefunden wird.

    Returns:
        User: Das `User`-Objekt aus der Datenbank, das dem gültigen Token entspricht.
    """
    # Definition der Exception die gegeben wird, wenn ein Fehler auftritt
    credentials_exception = HTTPException(
        status_code=401,  # Status UNAUTHORIZED
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Der Token wird dekodiert anhand der JWT config
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Der Nutzername wird aus dem Token entnommen ('sub' = Subject)
        username: str | None = payload.get("sub")
        # Wenn der Token keinen Nutzernamen enthält
        if username is None:
            # Gib die Exception zurück
            raise credentials_exception
    # Wenn der gegebene Token nicht valide ist
    except InvalidTokenError as e:
        # Gib die Exception zurück
        raise credentials_exception from e
    # Nutzer wird aus Datenbank abgefragt
    user = get_user(username=username)
    # Wenn Nutzer nicht existiert
    if user is None:
        # Gib die Exception zurück
        raise credentials_exception
    # Gib das gefundene Nutzer-Objekt zurück
    return user


# endregion

# region ↓ API Endpunkte ↓

@app.post("/register", summary="Register a new user")
async def post_signup(user: User) -> Token:
    """Registriert einen neuen Benutzer im System.

    Args:
        user (User): Die Benutzerdaten aus dem Request Body.

    Returns:
        Token: Das Ergebnis der `register`-Funktion aus dem `user_service`.
               Ein Objekt bestehend aus access_token und token_type.
    """
    return register(user=user)


@app.post("/token", summary="Request an access token")
async def post_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """Authentifiziert einen Benutzer und gibt einen Access Token zurück.

    Nimmt Benutzername und Passwort als Formular-Daten entgegen
    und verwendet den user_service, um den Benutzer zu authentifizieren und
    einen JWT Access Token zu generieren.

    Args:
        form_data (Annotated[OAuth2PasswordRequestForm, Depends()]): Die Formular-Daten
            mit `username` und `password`.

    Returns:
        Token: Das Ergebnis der `register`-Funktion aus dem `user_service`.
               Ein Objekt bestehend aus access_token und token_type.
    """
    return login(form_data=form_data)


@app.get("/category", summary="Get random game categories")
async def get_category() -> list:
    """Gibt eine Liste von zufälligen Spielkategorien zurück.

    Returns:
        list: Eine Liste von Spielkategorien.
    """
    return random_category_list(count=2)


@app.get("/question", summary="Get random questions for a category")
async def get_question(category: int) -> list:
    """Gibt eine Liste von zufälligen Fragen für eine gegebene Kategorie-ID zurück.

    Args:
        category (int): Die ID der Kategorie als Query-Parameter (z.B. /question?category=1).

    Returns:
        list: Eine Liste von Fragen für die angegebene Kategorie.
    """
    return random_question_list(category=category, count=3)


@app.get("/score", summary="Get the leaderboard")
async def get_scores() -> list:
    """Gibt die Top-Rangliste (Leaderboard) der Benutzer-Scores zurück.

    Returns:
        list: Eine Liste von Ranglisten-Einträgen.
    """
    return get_leaderboard(count=10)


@app.patch("/user/score", summary="Update user score")
async def patch_score(
        current_user: Annotated[User, Depends(verify_user_token)],
        score: Score
) -> Score:
    """Aktualisiert den Score des aktuell authentifizierten Benutzers.

    Dieser Endpunkt ist geschützt und erfordert ein gültiges JWT Bearer Token.
    Nimmt ein Score-Objekt im Request Body entgegen und aktualisiert den Score
    des durch das Token identifizierten Benutzers über den `user_service`.

    Args:
        current_user (Annotated[User, Depends(verify_user_token)]): Der authentifizierte
            Benutzer, automatisch durch die `verify_user_token`-Abhängigkeit ermittelt.
        score (Score): Das Score-Objekt mit den neuen Score-Daten aus dem Request Body.

    Returns:
        Score: Das neue Ergebnis der `update_score`-Funktion aus dem `user_service`
    """
    # Stellt sicher, dass der Score für den authentifizierten Benutzer aktualisiert wird
    return update_score(username=current_user.username, score=score)


@app.get("/achievement", summary="Get all possible achievements")
async def get_achievements() -> list[Achievement]:
    """Gibt eine Liste aller im System definierten Achievements zurück.

    Returns:
        list[Achievement]: Eine Liste aller definierten `Achievement`-Objekte.
    """
    return all_achievements()


@app.get("/user/achievement", summary="Get achievements of current user")
async def get_user_achievements(
        current_user: Annotated[User, Depends(verify_user_token)]
) -> list[Achievement]:
    """Gibt eine Liste der Achievements zurück, die der aktuell authentifizierte Benutzer erreicht hat.

    Dieser Endpunkt ist geschützt und erfordert ein gültiges JWT Bearer Token.
    Ruft den `achievement_service` auf, um die Achievements des durch das Token
    identifizierten Benutzers abzurufen.

    Args:
        current_user (Annotated[User, Depends(verify_user_token)]): Der authentifizierte
            Benutzer, automatisch durch die `verify_user_token`-Abhängigkeit ermittelt.

    Returns:
        list[Achievement]: Eine Liste der `Achievement`-Objekte, die der Benutzer
                           bereits freigeschaltet hat.
    """
    return user_achievements(username=current_user.username)


@app.patch("/user/achievement", summary="Unlock an achievement for the current user")
async def patch_user_achievement(
        current_user: Annotated[User, Depends(verify_user_token)],
        achievement: Achievement  # Nimmt ID, Name, Beschreibung entgegen
) -> dict:
    """Schaltet ein Achievement für den aktuell authentifizierten Benutzer frei.

    Dieser Endpunkt ist geschützt und erfordert ein gültiges JWT Bearer Token.
    Nimmt die Daten eines Achievements im Request Body entgegen
    und verknüpft dieses Achievement über den `achievement_service`
    mit dem durch das Token identifizierten Benutzer.

    Args:
        current_user (Annotated[User, Depends(verify_user_token)]): Der authentifizierte
            Benutzer, automatisch durch die `verify_user_token`-Abhängigkeit ermittelt.
        achievement (Achievement): Das Achievement-Objekt aus dem Request Body,
                                   das freigeschaltet werden soll.

    Returns:
        dict: Das Ergebnis der `unlock_user_achievement`-Funktion aus dem
              `achievement_service` (Eine Erfolgsmeldung,
              oder eine Meldung, falls das Achievement bereits freigeschaltet war).
    """
    # Ruft den Service auf, um das Achievement für den Benutzer freizuschalten
    return unlock_user_achievement(username=current_user.username, achievement=achievement)

# endregion
