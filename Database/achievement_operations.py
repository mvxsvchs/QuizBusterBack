import psycopg

from Database.database import get_connection


# region ↓ Abfragen für "Achievement" Objekt ↓

# Klasse für Achievement wie in Datenbank
# pylint: disable=too-few-public-methods
class Achievement:
    # Constructor
    def __init__(self, achievement_id: int, name: str, description: str):
        self.achievement_id = achievement_id
        self.name = name
        self.description = description


# Erstelle Achievement Objekt aus Datenbank Satz
def create_achievement(achievement_result: list) -> list[Achievement]:
    result = list[Achievement]()
    for row in achievement_result:
        # Aus jedem Eintrag der Datenbank wird ein Objekt erstellt
        result.append(Achievement(achievement_id=int(row[0]), name=str(row[1]), description=str(row[2])))
    return result


def get_achievement_list() -> list[Achievement]:
    try:
        conn = get_connection()
        cur = conn.cursor()

        # SQL Abfrage zum Erhalten aller Achievements
        get_query = ('SELECT "ID", "name", "description" '
                     'FROM "Achievement";')
        cur.execute(get_query)
        # Alle Datensätze werden abgerufen
        result = cur.fetchall()

        cur.close()
        conn.close()

        # Der Datensatz im Listen-Format wird zu Objekt gewandelt
        return create_achievement(result)
    except Exception as error:
        # Gibt eine Fehlermeldung aus und wirft den Fehler erneut
        print("Fehler bei der Achievement Abfrage:", error)
        raise error


def get_user_achievement_list(username: str) -> list[Achievement]:
    try:
        conn = get_connection()
        cur = conn.cursor()

        # SQL Abfrage zum Erhalten aller Achievements des Nutzers
        get_query = ('SELECT "Achievement"."ID", "Achievement"."name", "Achievement"."description" '
                     'FROM "Achievement" '
                     'JOIN "User_Achievement" ON "Achievement"."ID" = "User_Achievement"."achievement_id"'
                     'WHERE "User_Achievement"."username"=%s;')
        cur.execute(get_query, (username,))
        # Alle Datensätze werden abgerufen
        result = cur.fetchall()

        cur.close()
        conn.close()

        # Der Datensatz im Listen-Format wird zu Objekt gewandelt
        return create_achievement(result)
    except Exception as error:
        # Gibt eine Fehlermeldung aus und wirft den Fehler erneut
        print("Fehler bei der Nutzer Achievement Abfrage:", error)
        raise error


def add_user_achievement(username: str, achievement_id: int):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # SQL Abfrage zum Hinzufügen des Achievements für den Nutzer
        insert_query = ('INSERT INTO "User_Achievement" ("username", "achievement_id")'
                        ' VALUES (%s, %s);')
        cur.execute(insert_query, (username, achievement_id))
        conn.commit()

        cur.close()
        conn.close()
        return {"message": "User achievement added."}
    # Der Nutzer hat in der Datenbank bereits dieses Achievement
    except psycopg.errors.UniqueViolation:
        print(f"User hat bereits das Achievement {achievement_id}")
        return {"message": "User achievement already exists."}
    except Exception as error:
        # Gibt eine Fehlermeldung aus und wirft den Fehler erneut
        print("Fehler bei hinzufügen des Nutzer Achievements:", error)
        raise error

# endregion
