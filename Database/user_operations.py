from Database.database import get_connection


class User:
    # Constructor
    def __init__(self, username, password):
        self.username = username
        self.password = password


def create_user(user_result: list) -> User:
    result = User(user_result[0], user_result[1])
    return result


def insert_user(username: str, password: str, role: str):
    try:
        conn = get_connection()
        cur = conn.cursor()

        insert_query = 'INSERT INTO "User" (username, password, role) VALUES (%s, %s, %s);'
        cur.execute(insert_query, (username, password, role))
        conn.commit()

        cur.close()
        conn.close()

    except Exception as error:
        print("Fehler beim Einfügen des Users:", error)
        raise error


def user_exists(username: str) -> bool:
    try:
        conn = get_connection()
        cur = conn.cursor()

        # SQL-Abfrage zur Überprüfung, ob der Benutzer existiert (1 ist ein Platzhalter)
        get_query = 'SELECT 1 FROM "User" WHERE username = %s;'
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


def get_user(username: str) -> User:
    try:
        conn = get_connection()
        cur = conn.cursor()

        get_query = 'SELECT "username", "password" FROM "User" WHERE username = %s;'
        cur.execute(get_query, (username,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        return create_user(user)
    except Exception as error:
        # Gibt eine Fehlermeldung aus und wirft den Fehler erneut
        print("Fehler bei der Benutzerprüfung:", error)
        raise error
