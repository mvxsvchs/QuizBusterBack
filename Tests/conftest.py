import pytest
import psycopg
from psycopg import OperationalError

from Config.postgres_config import *


# Stellt eine Verbindung zur TEST-Datenbank her
def get_test_db_connection():
    try:
        conn = psycopg.connect(
            host=TEST_DB_IP,
            port=TEST_DB_PORT,
            dbname=TEST_DATABASE,
            user=TEST_DB_USERNAME,
            password=TEST_DB_PASSWORD,
            autocommit=True
        )
        return conn
    except OperationalError as e:
        print(f"FEHLER: Konnte keine Verbindung zur Test-DB '{TEST_DATABASE}' herstellen")
        pytest.exit(f"Test-DB Verbindung fehlgeschlagen: {e}", returncode=1)


# Erstellt die Test-Datenbank einmal pro Session, falls sie noch nicht existiert
@pytest.fixture(scope="session", autouse=True)
def create_test_database_if_not_exists():
    conn = None
    try:
        conn = get_test_db_connection()
        cur = conn.cursor()
        get_query = ('SELECT 1 '
                     'FROM pg_database '
                     'WHERE datname = %s')
        cur.execute(get_query, (TEST_DATABASE,))
        exists = cur.fetchone()
        if not exists:
            print(f"Erstelle Test-Datenbank: {TEST_DATABASE}...")
            create_query = f'CREATE DATABASE "{TEST_DATABASE}"'
            cur.execute(create_query)
            print("Test-Datenbank erstellt.")
        else:
            print(f"Test-Datenbank '{TEST_DATABASE}' existiert bereits.")
    except Exception as e:
        print(f"FEHLER beim Erstellen der Test-DB '{TEST_DATABASE}': {e}")
    finally:
        if conn:
            # Verbindung schließen
            conn.close()


# Diese Fixture läuft vor und nach JEDEM Test
# Sie stellt sicher, dass die benötigten Tabellen existieren und leer sind.
@pytest.fixture(scope="function", autouse=True)
def manage_test_db_data():
    try:
        # Stellt Verbindung her & schließt sie automatisch
        with get_test_db_connection() as conn:
            # Erstellt Cursor & schließt ihn automatisch
            with conn.cursor() as cur:
                # Stellt sicher, dass die Tabelle existiert
                create_query = ('CREATE TABLE IF NOT EXISTS "User" ('
                                'username VARCHAR(100) PRIMARY KEY,'
                                'password VARCHAR(255) NOT NULL,'
                                'score INTEGER);')
                cur.execute(create_query)

                # Leert die Tabelle vor dem Test
                clear_query = 'TRUNCATE TABLE "User" RESTART IDENTITY CASCADE;'
                cur.execute(clear_query)

                conn.commit()
                print("Test-DB Tabellen bereit und geleert für den Test")

            yield
    except Exception as e:
        print(f"FEHLER während des Test-DB Setups: {e}")
        raise
