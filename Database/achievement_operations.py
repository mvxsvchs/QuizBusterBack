"""Modul für Datenbankoperationen im Zusammenhang mit Achievements.

Dieses Modul definiert die `Achievement`-Datenstruktur und stellt Funktionen
bereit, um Achievements aus der Datenbank abzurufen und einem Benutzer neue Achievements zuzuweisen.
Es nutzt die `psycopg`-Bibliothek und die zentrale `get_connection`-Funktion
für die Datenbankverbindung.
"""
from psycopg import errors as psycopg_errors
from Database.database import get_connection


# region ↓ Abfragen für "Achievement" Objekt ↓

# pylint: disable=too-few-public-methods
class Achievement:
    """Repräsentiert ein einzelnes Achievement aus der Datenbank.

    Attributes:
        achievement_id (int): Eindeutige ID des Achievements.
        name (str): Name des Achievements.
        description (str): Beschreibung des Achievements.
    """

    # Constructor
    def __init__(self, achievement_id: int, name: str, description: str):
        """Initialisiert ein neues Achievement-Objekt."""
        self.achievement_id = achievement_id
        self.name = name
        self.description = description


def create_achievement(achievement_result: list) -> list[Achievement]:
    """Wandelt eine Liste von Datenbank-Zeilen in eine Liste von Achievement-Objekten um.

    Iteriert durch die Ergebnisliste einer Datenbankabfrage
    und erstellt für jede Zeile ein `Achievement`-Objekt.

    Args:
        achievement_result (list): Eine Liste von Listen, wie sie von
                                   `cursor.fetchall()` zurückgegeben wird. Jedes
                                   innere Element sollte die Daten für ein Achievement
                                   in der Reihenfolge (ID, Name, Beschreibung) enthalten.

    Returns:
        list[Achievement]: Eine Liste von `Achievement`-Instanzen. Gibt eine leere
                           Liste zurück, wenn die Eingabeliste leer ist.
    """
    result: list[Achievement] = []
    for row in achievement_result:
        # Aus jedem Eintrag der Datenbank wird ein Objekt erstellt
        result.append(
            Achievement(
                achievement_id=int(row[0]),
                name=str(row[1]),
                description=str(row[2])
            )
        )
    return result


def get_achievement_list() -> list[Achievement]:
    """Ruft alle verfügbaren Achievements aus der Datenbank ab.

    Returns:
        list[Achievement]: Eine Liste aller `Achievement`-Objekte aus der Datenbank.
                           Gibt eine leere Liste zurück, wenn keine Achievements
                           gefunden werden.

    Raises:
        psycopg.OperationalError: Wenn die Datenbankverbindung fehlschlägt.
        Exception: Bei anderen Fehlern während der Datenbankabfrage oder Verarbeitung.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # SQL Abfrage zum Erhalten aller Achievements
        get_query = ('SELECT "ID", "name", "description" '
                     'FROM "Achievement";')
        cur.execute(query=get_query)
        # Alle Datensätze werden abgerufen
        db_result = cur.fetchall()

        # Verbindung nach Gebrauch schließen
        cur.close()
        conn.close()

        # Der Datensatz im Listen-Format wird zu Objekt gewandelt
        return create_achievement(db_result)
    except Exception as error:
        # Gibt eine Fehlermeldung aus und wirft den Fehler erneut
        print(f"Fehler bei der Achievement Abfrage: {error}")
        # Sicherstellen, dass die Verbindung geschlossen wird, auch im Fehlerfall
        if conn and not conn.closed:
            conn.close()
        raise error


def get_user_achievement_list(username: str) -> list[Achievement]:
    """Ruft alle Achievements ab, die ein bestimmter Benutzer erreicht hat.

    Args:
        username (str): Der Benutzername, dessen Achievements abgerufen werden sollen.

    Returns:
        list[Achievement]: Eine Liste der `Achievement`-Objekte, die der Benutzer
                           erreicht hat. Gibt eine leere Liste zurück, wenn der
                           Benutzer keine Achievements hat.

    Raises:
        psycopg.OperationalError: Wenn die Datenbankverbindung fehlschlägt.
        Exception: Bei anderen Fehlern während der Datenbankabfrage oder Verarbeitung.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # SQL Abfrage zum Erhalten aller Achievements des Nutzers
        get_query = ('SELECT a."ID", a."name", a."description" '
                     'FROM "Achievement" a '
                     'JOIN "User_Achievement" ua '
                     'ON a."ID" = ua."achievement_id"'
                     'WHERE ua."username"=%s;')
        cur.execute(query=get_query, params=(username,))
        # Alle Datensätze werden abgerufen
        db_result = cur.fetchall()

        # Verbindung nach Gebrauch schließen
        cur.close()
        conn.close()

        # Der Datensatz im Listen-Format wird zu Objekt gewandelt
        return create_achievement(db_result)
    except Exception as error:
        # Gibt eine Fehlermeldung aus und wirft den Fehler erneut
        print(f"Fehler bei der Nutzer Achievement Abfrage für '{username}': {error}")
        # Sicherstellen, dass die Verbindung geschlossen wird, auch im Fehlerfall
        if conn and not conn.closed:
            conn.close()
        raise error


def add_user_achievement(username: str, achievement_id: int) -> dict:
    """Fügt einem Benutzer ein bestimmtes Achievement hinzu.

    Args:
        username (str): Der Benutzername des Benutzers.
        achievement_id (int): Die ID des Achievements, das hinzugefügt werden soll.

    Returns:
        dict: Ein Dictionary, das den Erfolg
              (`{"message": "User achievement added."}`)
              oder das Vorhandensein des Eintrags
              (`{"message": "User achievement already exists."}`)
              anzeigt.

    Raises:
        psycopg.OperationalError: Wenn die Datenbankverbindung fehlschlägt.
        Exception: Bei anderen Fehlern während der Datenbankoperation.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # SQL Abfrage zum Hinzufügen des Achievements für den Nutzer
        insert_query = (
            'INSERT INTO "User_Achievement" ("username", "achievement_id")'
            ' VALUES (%s, %s);'
        )
        cur.execute(query=insert_query, params=(username, achievement_id))
        conn.commit()

        # Verbindung nach Gebrauch schließen
        cur.close()
        conn.close()
        return {"message": "User achievement added."}
    # Der Nutzer hat in der Datenbank bereits dieses Achievement
    except psycopg_errors.UniqueViolation:
        print(f"User '{username}' hat bereits das Achievement {achievement_id}")
        if conn and not conn.closed:
            # Sicherstellen, dass die Verbindung geschlossen wird, auch im Fehlerfall
            conn.close()
        return {"message": "User achievement already exists."}
    except Exception as error:
        print(f"Fehler bei hinzufügen des Nutzer Achievements "
              f"({username}, {achievement_id}): {error}")
        if conn and not conn.closed:
            # Sicherstellen, dass die Verbindung geschlossen wird, auch im Fehlerfall
            conn.close()
        raise error

# endregion
