"""Modul für Datenbankoperationen bezüglich Benutzerdaten und Scores.

Dieses Modul enthält Funktionen für den direkten Zugriff auf die Datenbanktabelle "User".
Es stellt Methoden zum Einfügen, Abrufen, Überprüfen der Existenz und Aktualisieren
von Benutzerdaten sowie zum Abrufen der Rangliste (Scores) bereit.
Es definiert auch Datenmodellklassen (`UserModel`, `ScoreModel`), die Datenbankzeilen repräsentieren.
"""

from typing import List, Optional

import psycopg

from Database.database import get_connection


# region ↓ Abfragen für "Nutzer" Objekt ↓

# pylint: disable=too-few-public-methods
class UserModel:
    """Repräsentiert einen Benutzerdatensatz, wie er aus der Datenbank gelesen wird."""

    # Constructor
    def __init__(self, username: str, password: str, score: Optional[int]):
        """Initialisiert ein neues UserModel-Objekt.

        Args:
            username (str): Der Benutzername.
            password (str): Das in der Datenbank gespeicherte Passwort (gehasht).
            score (Optional[int]): Der aktuelle Punktestand des Benutzers (kann None sein).
        """
        self.username = username
        self.password = password
        self.score = score


def create_user(user_result: list) -> UserModel:
    """Erstellt ein `UserModel`-Objekt aus einer einzelnen Datenbank-Zeile.

    Args:
        user_result (list): Eine Liste, die eine Zeile aus der User-Tabelle
            repräsentiert (erwartete Reihenfolge: username, password, score).

    Returns:
        UserModel: Das erstellte `UserModel`-Objekt.
    """
    # Erwartet username, password (hash), score
    return UserModel(
        username=str(user_result[0]),
        password=str(user_result[1]),
        # Score könnte NULL sein in der DB, daher ggf. None
        score=int(user_result[2]) if user_result[2] is not None else None
    )


def insert_user(username: str, password: str, role: str) -> None:
    """Fügt einen neuen Benutzerdatensatz in die "User"-Tabelle ein.

    Args:
        username (str): Der Benutzername für den neuen Benutzer.
        password (str): Der gehashte Passwort-String für den neuen Benutzer.
        role (str): Die Rolle des neuen Benutzers ('user', 'admin').

    Raises:
        psycopg.OperationalError: Bei Verbindungsproblemen.
        Exception: Bei anderen unerwarteten Datenbankfehlern.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # SQL-Abfrage zum Hinzufügen der Nutzerdaten
        insert_query = ('INSERT INTO "User" ("username", "password", "role")'
                        ' VALUES (%s, %s, %s);')
        cur.execute(insert_query, (username, password, role))
        conn.commit()

        # Verbindung nach Gebrauch schließen
        cur.close()
        conn.close()
    except Exception as error:
        print(f"Fehler beim Erstellen des Users '{username}': {error}")
        # Sicherstellen, dass die Verbindung geschlossen wird, auch im Fehlerfall
        if conn and not conn.closed:
            conn.close()
        raise error  # Fehler weiterleiten


def user_exists(username: str) -> bool:
    """Überprüft, ob ein Benutzer mit dem angegebenen Benutzernamen existiert.

    Args:
        username (str): Der zu überprüfende Benutzername.

    Returns:
        bool: True, wenn ein Benutzer mit diesem Namen existiert, sonst False.

    Raises:
        psycopg.OperationalError: Bei Verbindungsproblemen.
        Exception: Bei anderen unerwarteten Datenbankfehlern.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # SQL-Abfrage zur Überprüfung, ob der Benutzer existiert
        # SELECT 1 ist effizienter als SELECT * oder SELECT username
        get_query = ('SELECT 1 FROM "User" WHERE "username" = %s;')
        cur.execute(get_query, (username,))

        # Wenn fetchone() ein Ergebnis liefert (egal was), existiert der Benutzer
        exists = cur.fetchone() is not None

        # Verbindung nach Gebrauch schließen
        cur.close()
        conn.close()

        return exists
    except Exception as error:
        print(f"Fehler bei der Benutzerprüfung für '{username}': {error}")
        # Sicherstellen, dass die Verbindung geschlossen wird, auch im Fehlerfall
        if conn and not conn.closed:
            conn.close()
        raise error


def get_user_data(username: str, connection: Optional[psycopg.Connection] = None) -> UserModel:
    """Ruft die Daten eines Benutzers aus der Datenbank ab.

    Ermöglicht die Übergabe einer bestehenden Datenbankverbindung für Transaktionen.
    Wenn keine Verbindung übergeben wird, wird eine neue aufgebaut und geschlossen.

    Args:
        username (str): Der Benutzername des gesuchten Benutzers.
        connection (Optional[psycopg.Connection]): Eine optional bestehende
            psycopg-Datenbankverbindung. Wenn None, wird eine neue erstellt.

    Returns:
        UserModel: Ein `UserModel`-Objekt mit den Benutzerdaten,
                   falls der Benutzer gefunden wurde, sonst `None`.

    Raises:
        psycopg.OperationalError: Bei Verbindungsproblemen.
        Exception: Bei anderen unerwarteten Datenbankfehlern.
    """
    conn = None
    try:
        # Verwende übergebene Verbindung oder hole eine neue
        if connection is None:
            conn = get_connection()
        else:
            conn = connection

        cur = conn.cursor()

        # SQL Abfrage zum Erhalten der Nutzerdaten für den Nutzernamen
        get_query = ('SELECT "username", "password", "score" '
                     'FROM "User" WHERE "username" = %s;')
        cur.execute(get_query, (username,))
        # Nur ein Datensatz wird abgerufen
        user_data_tuple = cur.fetchone()

        # Verbindung nach Gebrauch schließen
        cur.close()
        conn.close()

        # Wandle das Ergebnis in ein UserModel um
        user_model = create_user(user_data_tuple)
        return user_model
    except Exception as error:
        print(f"Fehler bei dem Abruf der Benutzerdaten für '{username}': {error}")
        # Sicherstellen, dass die Verbindung geschlossen wird, auch im Fehlerfall
        if conn and not conn.closed:
            conn.close()
        raise error


# endregion

# region ↓ Abfragen für "score" Daten ↓

def update_points(username: str, points: int) -> int:
    """Aktualisiert den Punktestand eines Benutzers durch Addition der Punkte.

    Holt den aktuellen Benutzer, addiert die neuen Punkte zum vorhandenen Score
    (oder startet bei 0, wenn kein Score vorhanden war) und speichert den neuen
    Gesamtscore in der Datenbank.

    Args:
        username (str): Der Benutzername des Benutzers, dessen Score aktualisiert wird.
        points (int): Die Anzahl der Punkte, die zum aktuellen Score hinzugefügt werden sollen.

    Returns:
        int: Der neue Gesamtpunktestand des Benutzers nach dem Update.

    Raises:
        psycopg.OperationalError: Bei Verbindungsproblemen.
        Exception: Bei anderen unerwarteten Datenbankfehlern.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Nutzerdaten für Nutzernamen werden abgerufen
        # Dieselbe Verbindung wird verwendet,
        # um innerhalb derselben Transaktion zu bleiben
        user = get_user_data(username=username, connection=conn)

        # Zu dem bestehenden score wird das neue Ergebnis dazu addiert
        current_score = int(user.score or 0)
        updated_points = current_score + points

        # Das score Feld für den Nutzer wird mit dem neuen Wert ge-updated
        update_query = ('UPDATE "User" SET "score" = %s WHERE "username" = %s;')
        cur.execute(update_query, (updated_points, username,))
        conn.commit()

        # Verbindung nach Gebrauch schließen
        cur.close()
        conn.close()

        # Gibt den neu berechneten Gesamtscore zurück
        return updated_points
    except Exception as error:
        print(f"Fehler beim updaten der Punkte für '{username}': {error}")
        # Sicherstellen, dass die Verbindung geschlossen wird, auch im Fehlerfall
        if conn and not conn.closed:
            conn.close()
        raise error


# pylint: disable=too-few-public-methods
class ScoreModel:
    """Repräsentiert einen Eintrag in der Rangliste (Benutzername und Score)."""

    # Constructor
    def __init__(self, username: str, score: int):
        """Initialisiert ein neues ScoreModel-Objekt.

        Args:
            username (str): Der Benutzername.
            score (int): Der erreichte Punktestand.
        """
        self.username = username
        self.score = score


def create_score(user_result: list) -> list[ScoreModel]:
    """Wandelt eine Liste von DB-Zeilen (username, score) in `ScoreModel`-Objekte um.

    Args:
        user_result (list): Eine Liste, wie sie von
            `cursor.fetchall()` für die Rangliste zurückgegeben wird.

    Returns:
        list[ScoreModel]: Eine Liste von `ScoreModel`-Instanzen.
    """
    result: list[ScoreModel] = []
    for row in user_result:
        # Aus jedem Eintrag der Datenbank wird ein Objekt erstellt
        result.append(
            ScoreModel(
                username=str(row[0]),
                score=int(row[1])
            )
        )
    return result


def get_scores(limit: int) -> List[ScoreModel]:
    """Ruft die Top limit Ranglistenplätze (Benutzername und Score) aus der Datenbank ab.

    Args:
        limit (int): Die maximale Anzahl der zurückzugebenden Ranglistenplätze.

    Returns:
        List[ScoreModel]: Eine Liste der Top `ScoreModel`-Objekte, sortiert nach
                          Score absteigend.

    Raises:
        psycopg.OperationalError: Bei Verbindungsproblemen.
        Exception: Bei anderen unerwarteten Datenbankfehlern.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Rufe Nutzername und score für die top Nutzer in absteigender Reihenfolge ab
        # Nutzer ohne score werden herausgefiltert
        get_query = ('SELECT "username", "score" '
                     'FROM "User" '
                     'WHERE "score" IS NOT NULL '  # Nur Nutzer mit Score berücksichtigen
                     'ORDER BY "score" DESC '  # Höchster Score zuerst
                     'LIMIT %s;')  # Begrenze die Anzahl
        cur.execute(get_query, (limit,))
        db_results = cur.fetchall()

        # Verbindung nach Gebrauch schließen
        cur.close()
        conn.close()

        # Ergebnis wird in Objekt gewandelt
        score_models = create_score(db_results)

    except Exception as error:
        print(f"Fehler bei Abfrage der Top Scores (limit={limit}): {error}")
        # Sicherstellen, dass die Verbindung geschlossen wird, auch im Fehlerfall
        if conn and not conn.closed:
            conn.close()
        raise error
    return score_models

# endregion
