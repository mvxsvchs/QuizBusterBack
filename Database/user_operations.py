from Database.database import get_connection


def insert_user(username: str, password: str, role: str):
    try:
        conn = get_connection()

        cur = conn.cursor()

        # SQL INSERT mit Platzhaltern (%s)
        insert_query = 'INSERT INTO "User" (username, password, role) VALUES (%s, %s, %s);'
        cur.execute(insert_query, (username, password, role))

        conn.commit()

        cur.close()
        conn.close()

    except Exception as e:
        print("Fehler beim Einfügen des Users:", e)