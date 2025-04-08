"""Service-Modul für den Abruf von Spielinhalten (Kategorien & Fragen).

Es stellt einfache Funktionen bereit,
um eine bestimmte Anzahl zufälliger Kategorien oder Fragen für eine
spezifische Kategorie zu erhalten und um Fragen zu verwalten.
"""
import random

from fastapi import HTTPException

from Database.game_operations import (
    get_category_list,
    get_question_list,
    QuestionModel,
    CategoryModel,
    insert_question,
    question_exists,
    update_question,
    delete_question,
)
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


def create_new_question(question: Question) -> dict:
    """Fügt die gegebene Frage in die Datenbank ein.

    Args:
        question (Question): Die Frage die in die Datenbank
                             hinzugefügt werden soll.

    Returns:
        dict: Das Ergebnis der Funktion als einfache Nachricht.
    """
    return insert_question(question=question)


def update_existing_question(question_id: int, question: Question) -> dict:
    """Fügt die gegebenen Werte in die Frage mit der gegebenen id ein.

    Args:
        question_id (int): Die id der Frage die geupdatet werden soll.
        question (Question): Die neuen Werte der Frage die in die Datenbank
                             hinzugefügt werden sollen.

    Returns:
        dict: Das Ergebnis der Funktion als einfache Nachricht.
    """
    existing = question_exists(question_id=question_id)
    if existing:
        return update_question(question_id=question_id, question=question)
    else:
        raise HTTPException(status_code=404, detail=f"Frage {question_id} existiert nicht.")


def delete_existing_question(question_id: int) -> dict:
    """Löscht die Frage mit der gegebenen id.

    Args:
        question_id (int): Die id der Frage die gelöscht werden soll.

    Returns:
        dict: Das Ergebnis der Funktion als einfache Nachricht.
    """
    existing = question_exists(question_id=question_id)
    if existing:
        return delete_question(question_id=question_id)
    else:
        raise HTTPException(status_code=404, detail=f"Frage {question_id} existiert nicht.")

# endregion
