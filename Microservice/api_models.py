"""Modul zur Definition von API-Datenmodellen für die Anwendung.

Es definiert Modelle für:
- Benutzerdaten (`User`)
- Authentifizierungs-Tokens (`Token`)
- Quizfragen (`Question`)
- Punktestände (`Score`)
- Achievements (`Achievement`)
"""
from pydantic import BaseModel


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
class Question(BaseModel):
    """Repräsentiert ein Question Model, wie bei der API benötigt."""
    category_id: int
    question: str
    correct_answer: str
    incorrect_answers: list[str]


# pylint: disable=too-few-public-methods
class Score(BaseModel):
    """Repräsentiert Punktdaten für Updates."""
    points: int


# pylint: disable=too-few-public-methods
class Achievement(BaseModel):
    """Modell zur Repräsentation einer Achievement-Anfrage."""
    id: int
