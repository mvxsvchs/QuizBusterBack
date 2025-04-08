"""Modul zur Definition von Datenbank-Entitäten.

Definierte Modelle:
- `UserModel`: Repräsentiert einen Benutzerdatensatz aus der "User"-Tabelle.
- `CategoryModel`: Repräsentiert eine Kategorie aus der "Category"-Tabelle.
- `QuestionModel`: Repräsentiert eine Frage, potenziell mit Daten aus mehreren Tabellen.
- `ScoreModel`: Repräsentiert einen Eintrag für die Rangliste (username, score).
- `AchievementModel`: Repräsentiert ein Achievement aus der "Achievement"-Tabelle.
"""
from pydantic import BaseModel


# pylint: disable=too-few-public-methods
class UserModel(BaseModel):
    """Repräsentiert einen Benutzerdatensatz, wie er aus der Datenbank gelesen wird."""
    username: str
    password: str
    score: int | None


# pylint: disable=too-few-public-methods
class CategoryModel(BaseModel):
    """Repräsentiert eine Fragen-Kategorie aus der Datenbank."""
    category_id: int
    name: str


# pylint: disable=too-few-public-methods
class QuestionModel(BaseModel):
    """Repräsentiert eine einzelne Quizfrage mit Antworten."""
    category: str
    question: str
    correct_answer: str
    incorrect_answers: list[str]


# pylint: disable=too-few-public-methods
class ScoreModel(BaseModel):
    """Repräsentiert einen Eintrag in der Rangliste (Benutzername und Score)."""
    username: str
    score: int


# pylint: disable=too-few-public-methods
class AchievementModel(BaseModel):
    """Repräsentiert ein einzelnes Achievement aus der Datenbank."""
    achievement_id: int
    name: str
    description: str
