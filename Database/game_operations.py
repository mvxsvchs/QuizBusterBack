"""Modul für Datenbankoperationen im Zusammenhang mit Spielkategorien und Fragen.

Dieses Modul definiert Datenstrukturen (`Category`, `Question`) zur Repräsentation
von Spielinhalten und stellt Funktionen bereit, um diese aus der Datenbank abzurufen.

Abhängigkeiten:
- psycopg: Für die Datenbankverbindung.
- Database.database: Stellt die `get_connection`-Funktion bereit.
- random: Für die zufällige Auswahl von Elementen.
"""

import random

from pydantic import BaseModel

from Database.database import get_connection


# region ↓ Abfragen für "Kategorie" Objekt ↓

# pylint: disable=too-few-public-methods
class Category(BaseModel):
    """Repräsentiert eine Fragen-Kategorie aus der Datenbank."""
    category_id: int
    name: str


def create_category(category_result: list) -> list[Category]:
    """Wandelt eine Liste von Datenbank-Zeilen in Category-Objekte um.

    Iteriert durch die Ergebnisliste der Datenbankabfrage und erstellt für jede Zeile
    ein `Category`-Objekt. Erwartet die Spaltenreihenfolge:
    id, name.

    Args:
        category_result (list): Eine Liste, wie sie von
            `cursor.fetchall()` für Kategorien zurückgegeben wird.

    Returns:
        list[Category]: Eine Liste von `Category`-Instanzen.
    """
    result: list[Category] = []
    for row in category_result:
        # Aus jedem Eintrag der Datenbank wird ein Objekt erstellt
        result.append(
            Category(
                category_id=int(row[0]),
                name=str(row[1])
            )
        )
    return result


def get_category_list(count: int) -> list[Category]:
    """Ruft alle Kategorien ab und gibt eine zufällige Auswahl zurück.

    Args:
        count (int): Die Anzahl der zufällig auszuwählenden Kategorien.

    Returns:
        list[Category]: Eine Liste von `count` zufällig ausgewählten `Category`-Objekten.

    Raises:
        psycopg.OperationalError: Wenn die Datenbankverbindung fehlschlägt.
        Exception: Bei anderen Fehlern während der Abfrage oder Verarbeitung.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # SQL Abfrage zum Erhalten aller Kategorien
        get_query = ('SELECT "ID", "name" '
                     'FROM "Category";')
        cur.execute(get_query)
        # Alle Datensätze werden abgerufen
        all_results = cur.fetchall()

        # Verbindung nach Gebrauch schließen
        cur.close()
        conn.close()

        # Es werden zufällig gewählte Einträge aus der Liste gegeben
        random_values = random.sample(all_results, count)
        # Der Datensatz im Listen-Format wird zu Objekt gewandelt
        return create_category(random_values)
    except Exception as error:
        print(f"Fehler bei der Kategorie Abfrage: {error}")
        # Sicherstellen, dass die Verbindung geschlossen wird, auch im Fehlerfall
        if conn and not conn.closed:
            conn.close()
        raise error


# endregion

# region ↓ Abfragen für "Frage" Objekt ↓

# pylint: disable=too-few-public-methods
class Question(BaseModel):
    """Repräsentiert eine einzelne Quizfrage mit Antworten."""
    category: str
    question: str
    correct_answer: str
    incorrect_answers: list[str]


def create_question(question_result: list) -> list[Question]:
    """Wandelt eine Liste von Datenbank-Zeilen in Question-Objekte um.

    Iteriert durch die Ergebnisliste der Datenbankabfrage und erstellt für jede Zeile
    ein `Question`-Objekt. Erwartet die Spaltenreihenfolge:
    Kategoriename, Fragetext, korrekte Antwort, Liste falscher Antworten.

    Args:
        question_result (list): Eine Liste, wie sie von
            `cursor.fetchall()` für Fragen zurückgegeben wird.

    Returns:
        list[Question]: Eine Liste von `Question`-Instanzen.
    """
    result: list[Question] = []
    for row in question_result:
        # Aus jedem Eintrag der Datenbank wird ein Objekt erstellt
        result.append(
            Question(
                category=str(row[0]),
                question=str(row[1]),
                correct_answer=str(row[2]),
                incorrect_answers=row[3]
            )
        )
    return result


def get_question_list(category: int, count: int) -> list[Question]:
    """Ruft Fragen für eine Kategorie ab und gibt eine zufällige Auswahl zurück.

    Stellt eine Verbindung zur Datenbank her, fragt alle Fragen für die gegebene
    `category`-ID ab (inklusive Kategoriename), wählt zufällig `count` Einträge
    aus diesen Ergebnissen aus, schließt die Verbindung und gibt die ausgewählten
    Einträge als Liste von `Question`-Objekten zurück.

    Args:
        category (int): Die ID der Kategorie, für die Fragen abgerufen werden sollen.
        count (int): Die Anzahl der zufällig auszuwählenden Fragen.

    Returns:
        List[Question]: Eine Liste von `count` zufällig ausgewählten `Question`-Objekten
                       aus der angegebenen Kategorie.

    Raises:
        psycopg.OperationalError: Wenn die Datenbankverbindung fehlschlägt.
        Exception: Bei anderen Fehlern während der Abfrage oder Verarbeitung.
                   Der ursprüngliche Fehler wird weitergeworfen.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # SQL Abfrage zum Erhalten aller Fragen der Kategorie
        get_query = (
            'SELECT "Category"."name", "Question"."question_text", '
            '"Question"."correct_answer", "Question"."incorrect_answers" '
            'FROM "Question" '
            'JOIN "Category" ON "Category"."ID" = "Question"."category_id" '
            'WHERE "Question"."category_id" = %s;')
        cur.execute(get_query, (category,))
        # Alle Datensätze werden abgerufen
        all_results = cur.fetchall()

        # Verbindung nach Gebrauch schließen
        cur.close()
        conn.close()

        # Es werden zufällig gewählte Einträge aus der Liste gegeben
        random_values = random.sample(all_results, count)
        # Der Datensatz im Listen-Format wird zu Objekt gewandelt
        return create_question(random_values)
    except Exception as error:
        print(f"Fehler bei der Fragen Abfrage für Kategorie {category}: {error}")
        # Sicherstellen, dass die Verbindung geschlossen wird, auch im Fehlerfall
        if conn and not conn.closed:
            conn.close()
        raise error

# endregion
