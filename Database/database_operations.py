import psycopg
from Config.postgres_config import *

def insert_user(username: str, password: str, role: str):
    try:
        conn = psycopg.connect(
            host=ip,
            port=port,
            dbname=database,
            user=db_username,
            password=db_password
        )
        cur = conn.cursor()

        # SQL INSERT mit Platzhaltern (%s)
        insert_query = 'INSERT INTO "User" (username, password, role) VALUES (%s, %s, %s);'
        cur.execute(insert_query, (username, password, role))

        conn.commit()
        print(f"User '{username}' erfolgreich eingefügt!")

        cur.close()
        conn.close()

    except Exception as e:
        print("Fehler beim Einfügen des Users:", e)

insert_user("Maxi", "admin1", "admin")
