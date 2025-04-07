from Database.database import get_connection


# region ↓ Abfragen für "Nutzer" Objekt ↓

# Klasse für User wie in Datenbank
# pylint: disable=too-few-public-methods
class UserModel:
    # Constructor
    def __init__(self, username: str, password: str, score):
        self.username = username
        self.password = password
        self.score = score


# Erstelle User Objekt aus Datenbank Satz
def create_user(user_result: list) -> UserModel:
    result = UserModel(username=str(user_result[0]), password=str(user_result[1]), score=user_result[2])
    return result


def insert_user(username: str, password: str, role: str):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # SQL-Abfrage zum Hinzufügen der Nutzerdaten
        insert_query = ('INSERT INTO "User" ("username", "password", "role")'
                        ' VALUES (%s, %s, %s);')
        cur.execute(insert_query, (username, password, role))
        conn.commit()

        cur.close()
        conn.close()

    except Exception as error:
        print("Fehler beim Erstellen des Users:", error)
        raise error


def user_exists(username: str) -> bool:
    try:
        conn = get_connection()
        cur = conn.cursor()

        # SQL-Abfrage zur Überprüfung, ob der Benutzer existiert (1 ist ein Platzhalter)
        get_query = ('SELECT 1 '
                     'FROM "User" '
                     'WHERE "username" = %s;')
        cur.execute(get_query, (username,))

        # Wenn ein Ergebnis zurückkommt, existiert der Benutzer
        exists = cur.fetchone() is not None

        cur.close()
        conn.close()

        return exists
    except Exception as error:
        # Gibt eine Fehlermeldung aus und wirft den Fehler erneut
        print("Fehler bei der Benutzerprüfung:", error)
        raise error


def get_user_data(username: str, connection) -> UserModel:
    try:
        conn = connection or get_connection()
        cur = conn.cursor()

        # SQL Abfrage zum Erhalten der Nutzerdaten für den Nutzernamen
        get_query = ('SELECT "username", "password", "score" '
                     'FROM "User" '
                     'WHERE "username" = %s;')
        cur.execute(get_query, (username,))
        # Nur ein Datensatz wird abgerufen
        user = cur.fetchone()

        cur.close()
        if connection is None:
            conn.close()

        # Liste der Nutzerdaten wird zu einem Objekt gewandelt
        return create_user(user)
    except Exception as error:
        # Gibt eine Fehlermeldung aus und wirft den Fehler erneut
        print("Fehler bei dem Abruf der Benutzerdaten:", error)
        raise error


# endregion

# region ↓ Abfragen für "score" Daten ↓

def update_points(username: str, points: int) -> int:
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Nutzerdaten für Nutzernamen werden abgerufen
        user = get_user_data(username=username, connection=conn)
        # Zu dem bestehenden score wird das neue Ergebnis dazu addiert
        updated_points = int(user.score or 0) + points

        # Das score Feld für den Nutzer wird mit dem neuen Wert ge-updated
        update_query = ('UPDATE "User" '
                        'SET "score" = %s '
                        'WHERE "username" = %s;')
        cur.execute(update_query, (updated_points, username,))
        conn.commit()

        cur.close()
        conn.close()

        return updated_points
    except Exception as error:
        # Gibt eine Fehlermeldung aus und wirft den Fehler erneut
        print("Fehler beim updaten der Punkte:", error)
        raise error


# Klasse für Score des Nutzers
# pylint: disable=too-few-public-methods
class ScoreModel:
    # Constructor
    def __init__(self, username: str, score: int):
        self.username = username
        self.score = score


# Erstelle Score Objekt aus Datenbank Satz
def create_score(user_result: list) -> list[ScoreModel]:
    result = list[ScoreModel]()
    for row in user_result:
        # Aus jedem Eintrag der Datenbank wird ein Objekt erstellt
        result.append(ScoreModel(username=str(row[0]), score=int(row[1])))
    return result


def get_scores(limit: int) -> list[ScoreModel]:
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Rufe Nutzername und score für die top Nutzer in absteigender Reihenfolge ab
        # Nutzer ohne score werden herausgefiltert
        get_query = ('SELECT "username", "score" '
                     'FROM "User" '
                     'WHERE "score" IS NOT NULL '
                     'ORDER BY "score" DESC '
                     'LIMIT %s;')
        cur.execute(get_query, (limit,))
        result = cur.fetchall()

        cur.close()
        conn.close()

        # Ergebnis wird von Listenformat in Objekt gewandelt
        return create_score(result)
    except Exception as error:
        # Gibt eine Fehlermeldung aus und wirft den Fehler erneut
        print("Fehler bei Abfrage der Top Scores:", error)
        raise error

# endregion
