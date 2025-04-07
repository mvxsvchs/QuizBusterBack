"""Modul für Benutzer-Logik, Authentifizierung und Scoring.

Dieses Modul enthält die Logik für alle Operationen, die Benutzer betreffen.
"""
from datetime import datetime, timezone, timedelta
from typing import Annotated, Optional, Dict, Any

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext

# Importiert Konfiguration und Datenbankoperationen+Modelle
from Config.jwt_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from Database.user_operations import (
    insert_user,
    user_exists,
    get_user_data,
    update_points,
    UserModel,
    get_scores,
    ScoreModel,
)


# region ↓ API Modelle ↓

# pylint: disable=too-few-public-methods
class User(BaseModel):
    """Repräsentiert Benutzerdaten für Registrierung."""
    username: str
    password: str


# pylint: disable=too-few-public-methods
class Token(BaseModel):
    """Repräsentiert die JWT Access Token Antwort nach erfolgreichem Login+Registrierung."""
    access_token: str
    token_type: str


# pylint: disable=too-few-public-methods
class Score(BaseModel):
    """Repräsentiert Punktdaten für Updates."""
    points: int


# endregion

# region ↓ Passwort-Handling ↓

# Kontext zum Verschlüsseln des Passworts mit bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Erzeugt einen sicheren Hash für das übergebene Passwort mittels bcrypt.

    Args:
        password (str): Das Klartext-Passwort, das gehasht werden soll.

    Returns:
        str: Der resultierende Passwort-Hash als String.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Überprüft, ob ein Klartext-Passwort mit einem gespeicherten Hash übereinstimmt.

    Args:
        plain_password (str): Das vom Benutzer eingegebene Klartext-Passwort.
        hashed_password (str): Der in der Datenbank gespeicherte Hash.

    Returns:
        bool: True, wenn das Passwort korrekt ist, andernfalls False.
    """
    return pwd_context.verify(plain_password, hashed_password)


# endregion


# region ↓ Benutzer-Operationen ↓

def get_user(username: str) -> Optional[UserModel]:
    """Ruft Benutzerdaten aus der Datenbank ab.

    Args:
        username (str): Der Benutzername des gesuchten Benutzers.

    Returns:
        Optional[UserModel]: Das `UserModel`-Objekt, falls der Benutzer gefunden wurde.
    """
    return get_user_data(username=username)


def authenticate_user(username: str, password: str) -> Optional[UserModel]:
    """Authentifiziert einen Benutzer anhand von Benutzername und Passwort.

    Prüft, ob der Benutzer existiert und ob das angegebene Passwort mit dem
    gespeicherten Hash übereinstimmt.

    Args:
        username (str): Der Benutzername für den Login-Versuch.
        password (str): Das Passwort (Klartext) für den Login-Versuch.

    Returns:
        Optional[UserModel]: Das `UserModel`-Objekt des Benutzers bei erfolgreicher
                             Authentifizierung, andernfalls `None`.
    """
    user = get_user(username=username)
    # Prüft, ob der Benutzer existiert
    if not user:
        return None
    # Prüft, ob das Passwort korrekt ist
    if not verify_password(plain_password=password, hashed_password=user.password):
        return None
    # Wenn beides passt, gib das Benutzerobjekt zurück
    return user


# endregion

# region ↓ Token-Erstellung ↓

def create_access_token(data: Dict[str, Any]) -> str:
    """Erstellt einen JWT Access Token mit Ablaufdatum.

    Kodiert die übergebenen Daten (sollten 'sub' für den Benutzernamen enthalten)
    zusammen mit einem Ablaufdatum in ein JWT.

    Args:
        data (Dict[str, Any]): Ein Dictionary mit den Daten, die in den Token
                               aufgenommen werden sollen.

    Returns:
        str: Der kodierte JWT Access Token als String.
    """
    to_encode = data.copy()
    # Berechnet die Ablaufzeit in UTC
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Fügt das Ablaufdatum zum Payload hinzu
    to_encode.update({"exp": expire})
    # Kodiert den Payload zum Token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# endregion

# region ↓ Hauptfunktionen ↓

def register(user: User) -> Token:
    """Registriert einen neuen Benutzer im System.

    Überprüft, ob der Benutzername bereits vergeben ist. Wenn nicht, wird das
    Passwort gehasht, der Benutzer in der Datenbank gespeichert und ein
    Access Token für die erste Sitzung generiert.

    Args:
        user (User): Das API `User`-Modell mit `username` und `password`.

    Raises:
        HTTPException (409 Conflict): Wenn der angegebene `username` bereits existiert.

    Returns:
        Token: Ein API `Token`-Modell mit dem `access_token` und `token_type`.
    """
    if user_exists(username=user.username):
        raise HTTPException(status_code=409, detail="Benutzername bereits vergeben")

    # Passwort hashen und Benutzer speichern
    hashed_password = get_password_hash(user.password)
    insert_user(username=user.username, password=hashed_password, role="user")

    # Erstelle einen Access Token für den neu registrierten Benutzer
    access_token = create_access_token(data={"sub": user.username})

    # Gib das Token-Objekt zurück
    return Token(access_token=access_token, token_type="bearer")


def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """Authentifiziert einen Benutzer und generiert einen Access Token.

    Nimmt die Standard-OAuth2-Formulardaten entgegen, authentifiziert den Benutzer
    mittels `authenticate_user` und erstellt bei Erfolg einen JWT Access Token.

    Args:
        form_data (Annotated[OAuth2PasswordRequestForm, Depends()]): Von FastAPI bereitgestellte
            Formulardaten, die `username` und `password` enthalten.

    Raises:
        HTTPException (401 Unauthorized): Wenn die Authentifizierung fehlschlägt (Benutzer
                                         nicht gefunden oder Passwort falsch).

    Returns:
        Token: Ein API `Token`-Modell mit dem `access_token` und `token_type`.
    """
    user = authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        # Authentifizierung fehlgeschlagen
        raise HTTPException(
            status_code=401,
            detail="Falscher Nutzername oder Passwort",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Erstelle ein JWT Token bei erfolgreichem Login
    access_token = create_access_token(data={"sub": user.username})

    # Gib das Token-Objekt zurück
    return Token(access_token=access_token, token_type="bearer")


def update_score(username: str, score: Score) -> Score:
    """Aktualisiert den Punktestand (Score) eines Benutzers.

    Ruft die Datenbankfunktion `update_points` auf, um die Punkte zu aktualisieren.
    Die Funktion `update_points` gibt den neuen Gesamtpunktestand zurück.

    Args:
        username (str): Der Benutzername des Benutzers, dessen Score aktualisiert werden soll.
        score (Score): Das API `Score`-Modell, das die zu verarbeitenden Punkte enthält.

    Returns:
        Score: Das API `Score`-Modell, das den neuen Gesamtpunktestand des Benutzers
               nach der Aktualisierung enthält.
    """
    new_total_score = update_points(username=username, points=score.points)
    # Gib den neuen Gesamtscore als Score-Objekt zurück
    return Score(points=new_total_score)


def get_leaderboard(count: int) -> list[ScoreModel]:
    """Ruft die Top count Ranglistenplätze ab.

    Args:
        count (int): Die maximale Anzahl der zurückzugebenden Ranglistenplätze.

    Returns:
        list[ScoreModel]: Eine Liste vom Score Model mit dem Nutzernamen
                          und dem score.
    """
    return get_scores(limit=count)

# endregion
