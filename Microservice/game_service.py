"""Service-Modul für den Abruf von Spielinhalten (Kategorien & Fragen).

Es stellt einfache Funktionen bereit,
um eine bestimmte Anzahl zufälliger Kategorien oder Fragen für eine
spezifische Kategorie zu erhalten.
"""
from Database.game_operations import get_category_list, get_question_list, Question, Category


def random_category_list(count: int) -> list[Category]:
    """Ruft eine Liste mit einer zufälligen Auswahl an Kategorien ab.

    Diese Funktion dient als Wrapper für 'get_category_list' und fordert
    eine bestimmte Anzahl zufällig ausgewählter Kategorien aus der Datenbank an.

    Args:
        count (int): Die Anzahl der zufällig auszuwählenden Kategorien.

    Returns:
        list: Eine Liste mit den zufällig ausgewählten Kategorien.
    """

    return get_category_list(count=count)


def random_question_list(category: int, count: int) -> list[Question]:
    """Ruft eine Liste mit einer zufälligen Auswahl an Fragen für eine bestimmte Kategorie ab.

    Diese Funktion dient als Wrapper für 'get_question_list' und fordert
    eine bestimmte Anzahl zufällig ausgewählter Fragen für die angegebene
    Kategorie-ID aus der Datenbank an.

    Args:
        category (int): Die ID der Kategorie, aus der Fragen ausgewählt werden sollen.
        count (int): Die Anzahl der zufällig auszuwählenden Fragen aus dieser Kategorie.

    Returns:
        list: Eine Liste mit den zufällig ausgewählten Fragen aus der angegebenen Kategorie.
    """

    return get_question_list(category=category, count=count)
