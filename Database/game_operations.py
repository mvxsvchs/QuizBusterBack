"""Modul für Datenbankoperationen im Zusammenhang mit Spielkategorien und Fragen.

Dieses Modul definiert Datenstrukturen (`Category`, `Question`) zur Repräsentation
von Spielinhalten und stellt Funktionen bereit, um diese aus der Datenbank abzurufen.

Abhängigkeiten:
- psycopg: Für die Datenbankverbindung.
- Database.database: Stellt die `get_connection`-Funktion bereit.
"""

from Database.database import get_connection
from Database.db_models import QuestionModel, CategoryModel
from Microservice.api_models import Question


# region ↓ Abfragen für "Kategorie" Objekt ↓


def create_category(category_result: list) -> list[CategoryModel]:
    """Wandelt eine Liste von Datenbank-Zeilen in Category-Objekte um.

    Iteriert durch die Ergebnisliste der Datenbankabfrage und erstellt für jede Zeile
    ein `Category`-Objekt. Erwartet die Spaltenreihenfolge:
    id, name.

    Args:
        category_result (list): Eine Liste, wie sie von
            `cursor.fetchall()` für Kategorien zurückgegeben wird.

    Returns:
        list[CategoryModel]: Eine Liste von `Category`-Instanzen.
    """
    result: list[CategoryModel] = []
    for row in category_result:
        # Aus jedem Eintrag der Datenbank wird ein Objekt erstellt
        result.append(
            CategoryModel(
                category_id=int(row[0]),
                name=str(row[1])
            )
        )
    return result


def get_category_list() -> list[CategoryModel]:
    """Ruft alle Kategorien ab und gibt sie als Objekt zurück.

    Returns:
        list[CategoryModel]: Eine Liste von allen `Category`-Objekten.

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

        # Der Datensatz im Listen-Format wird zu Objekt gewandelt
        return create_category(all_results)
    except Exception as error:
        print(f"Fehler bei der Kategorie Abfrage: {error}")
        # Sicherstellen, dass die Verbindung geschlossen wird, auch im Fehlerfall
        if conn and not conn.closed:
            conn.close()
        raise error


# endregion

# region ↓ Abfragen für "Frage" Objekt ↓


def create_question(question_result: list) -> list[QuestionModel]:
    """Wandelt eine Liste von Datenbank-Zeilen in Question-Objekte um.

    Iteriert durch die Ergebnisliste der Datenbankabfrage und erstellt für jede Zeile
    ein `Question`-Objekt. Erwartet die Spaltenreihenfolge:
    Kategoriename, Fragetext, korrekte Antwort, Liste falscher Antworten.

    Args:
        question_result (list): Eine Liste, wie sie von
            `cursor.fetchall()` für Fragen zurückgegeben wird.

    Returns:
        list[QuestionModel]: Eine Liste von `Question`-Instanzen.
    """
    result: list[QuestionModel] = []
    for row in question_result:
        # Aus jedem Eintrag der Datenbank wird ein Objekt erstellt
        result.append(
            QuestionModel(
                category=str(row[0]),
                question=str(row[1]),
                correct_answer=str(row[2]),
                incorrect_answers=row[3]
            )
        )
    return result


def get_question_list(category: int) -> list[QuestionModel]:
    """Ruft alle Fragen für eine Kategorie ab.

    Args:
        category (int): Die ID der Kategorie, für die Fragen abgerufen werden sollen.

    Returns:
        List[Question]: Eine Liste von allen `Question`-Objekten
                       aus der angegebenen Kategorie.

    Raises:
        psycopg.OperationalError: Wenn die Datenbankverbindung fehlschlägt.
        Exception: Bei anderen Fehlern während der Abfrage oder Verarbeitung.
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

        # Der Datensatz im Listen-Format wird zu Objekt gewandelt
        return create_question(all_results)
    except Exception as error:
        print(f"Fehler bei der Fragen Abfrage für Kategorie {category}: {error}")
        # Sicherstellen, dass die Verbindung geschlossen wird, auch im Fehlerfall
        if conn and not conn.closed:
            conn.close()
        raise error


def insert_question(question: Question) -> QuestionModel:
    """Fügt die gegebene Frage in die Datenbank ein.

    Args:
        question (Question): Die Frage die angelegt werden soll.

    Returns:
        QuestionModel: Die angelegte Frage.

    Raises:
        psycopg.OperationalError: Wenn die Datenbankverbindung fehlschlägt.
        Exception: Bei anderen Fehlern während der Abfrage oder Verarbeitung.
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

        # Der Datensatz im Listen-Format wird zu Objekt gewandelt
        return create_question(all_results)
    except Exception as error:
        print(f"Fehler bei der Fragen Abfrage für Kategorie {category}: {error}")
        # Sicherstellen, dass die Verbindung geschlossen wird, auch im Fehlerfall
        if conn and not conn.closed:
            conn.close()
        raise error

# endregion
