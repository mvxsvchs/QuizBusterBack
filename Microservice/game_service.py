"""Service-Modul für den Abruf von Spielinhalten (Kategorien & Fragen).

Es stellt einfache Funktionen bereit,
um eine bestimmte Anzahl zufälliger Kategorien oder Fragen für eine
spezifische Kategorie zu erhalten.
"""
import random

from Database.game_operations import get_category_list, get_question_list, QuestionModel, CategoryModel
from Microservice.api_models import Question


# region ↓ Category methods ↓

def all_category_list() -> list[CategoryModel]:
    """Ruft eine Liste mit allen Kategorien ab.

    Returns:
        list: Eine Liste mit den zufällig ausgewählten Kategorien.
    """
    return get_category_list()


def random_category_list(count: int) -> list[CategoryModel]:
    """Ruft eine Liste mit allen Kategorien ab und gibt eine zufällige Auswahl zurück.

    Diese Funktion fordert alle Kategorien aus der Datenbank an
    und wählt zufällig `count` Einträge aus diesen Ergebnissen aus.

    Args:
        count (int): Die Anzahl der zufällig auszuwählenden Kategorien.

    Returns:
        list: Eine Liste mit den zufällig ausgewählten Kategorien.
    """
    results = get_category_list()
    # Es werden zufällig gewählte Einträge aus der Liste gegeben
    random_values = random.sample(results, count)

    return random_values


# endregion

# region ↓ Question methods ↓


def all_question_list(category: int, ) -> list[QuestionModel]:
    """Ruft eine Liste mit allen Fragen für eine bestimmte Kategorie ab..

    Args:
        category (int): Die ID der Kategorie, aus der Fragen abgerufen werden sollen.

    Returns:
        list: Eine Liste mit den zufällig ausgewählten Fragen aus der angegebenen Kategorie.
    """
    return get_question_list(category=category)


def random_question_list(category: int, count: int) -> list[QuestionModel]:
    """Ruft eine Liste mit allen Fragen für eine bestimmte Kategorie ab
       und gibt eine zufällige Auswahl zurück.

    Diese Funktion fordert alle Fragen für die angegebene Kategorie-ID aus der Datenbank an
    und wählt zufällig `count` Einträge aus diesen Ergebnissen aus.

    Args:
        category (int): Die ID der Kategorie, aus der Fragen ausgewählt werden sollen.
        count (int): Die Anzahl der zufällig auszuwählenden Fragen aus dieser Kategorie.

    Returns:
        list: Eine Liste mit den zufällig ausgewählten Fragen aus der angegebenen Kategorie.
    """

    results = get_question_list(category=category)
    # Es werden zufällig gewählte Einträge aus der Liste gegeben
    random_values = random.sample(results, count)
    return random_values


def create_new_question(question: Question) -> QuestionModel:
    """Fügt die gegebene Frage in die Datenbank ein.

    Args:
        question (Question): Die Frage die in die Datenbank
                             hinzugefügt werden soll.

    Returns:
        QuestionModel: Die neu angelegte Frage.
    """
    return get_question_list(category=category)

# endregion
