"""Modul zur Verwaltung der Test-Datenbankumgebung.

Es enthält:
- Eine Hilfsfunktion zum Herstellen einer Verbindung zur Test-Datenbank.
- Eine Session-Scoped Fixture (`create_test_database_if_not_exists`), die sicherstellt,
  dass die Test-Datenbank zu Beginn der Test-Session existiert.
- Eine Function-Scoped Fixture (`manage_test_db_data`), die vor jedem einzelnen Test
  läuft, um sicherzustellen, dass die benötigten Tabellen existieren und leer sind.

Abhängigkeiten:
- pytest: Für das Fixture-System.
- psycopg: Für die PostgreSQL-Datenbankinteraktion.
- Config.postgres_config: Beinhaltet die Verbindungsdetails für die Test-Datenbank
  (TEST_DB_IP, TEST_DB_PORT, etc.).
"""

import pytest
import psycopg
from psycopg import OperationalError

from Config.postgres_config import TEST_DB_IP, TEST_DB_PORT, TEST_DATABASE, TEST_DB_USERNAME, TEST_DB_PASSWORD


def get_test_db_connection() -> psycopg.Connection:
    """Stellt eine Verbindung zur PostgreSQL-Testdatenbank her.

    Returns:
        psycopg.Connection: Ein aktives Verbindungsobjekt zur Test-DB.

    Raises:
        SystemExit: Wird über `pytest.exit` ausgelöst, wenn die Verbindung fehlschlägt.
    """
    try:
        conn = psycopg.connect(
            host=TEST_DB_IP,
            port=TEST_DB_PORT,
            dbname=TEST_DATABASE,
            user=TEST_DB_USERNAME,
            password=TEST_DB_PASSWORD,
            autocommit=True
        )
        print(f"Verbindung zur Test-DB '{TEST_DATABASE}' erfolgreich hergestellt.")
        return conn
    except OperationalError as e:
        print(f"FEHLER: Konnte keine Verbindung zur Test-DB '{TEST_DATABASE}' herstellen: {e}")
        # Beendet den Pytest-Lauf, da Tests ohne DB-Verbindung nicht sinnvoll sind
        pytest.exit(f"Test-DB Verbindung fehlgeschlagen: {e}", returncode=1)


# Diese Fixture wird einmal pro Test-Session ausgeführt (`scope="session"`)
# und automatisch vor allen Tests (`autouse=True`).
@pytest.fixture(scope="session", autouse=True)
def create_test_database_if_not_exists():
    """Pytest Session-Fixture: Erstellt die Test-DB, falls sie nicht existiert.

    Versucht eine Verbindung zur konfigurierten Test-Datenbank herzustellen.
    Wenn erfolgreich, prüft sie in `pg_database`, ob der Eintrag existiert.
    Falls die Datenbank nicht existiert (was durch den vorherigen Verbindungsversuch
    eigentlich schon fehlschlagen sollte, es sei denn, man verbindet sich
    zuerst zu einer Standard-DB wie 'postgres'), versucht sie, die Test-DB
    zu erstellen.
    """
    conn = None
    try:
        # Versucht, sich initial zu verbinden (könnte schon fehlschlagen, wenn DB fehlt)
        print(f"Prüfe Existenz der Test-DB '{TEST_DATABASE}'...")
        conn = get_test_db_connection()
        cur = conn.cursor()

        # Prüfe, ob die Datenbank existiert
        get_query = ('SELECT 1 FROM pg_database WHERE datname = %s')
        cur.execute(get_query, (TEST_DATABASE,))
        exists = cur.fetchone()

        if not exists:
            print(f"Test-Datenbank '{TEST_DATABASE}' nicht gefunden.")
            print(f"Versuche Test-Datenbank zu erstellen: {TEST_DATABASE}...")
            cur.execute(f'CREATE DATABASE "{TEST_DATABASE}"')
        else:
            print(f"Test-Datenbank '{TEST_DATABASE}' existiert bereits.")

        cur.close()

    except Exception as e:
        print(f"FEHLER während der Test-DB-Erstellung: {e}")
        # Beendet den Pytest-Lauf
        pytest.exit(f"Fehler bei Test-DB Setup: {e}", returncode=1)
    finally:
        if conn and not conn.closed:
            conn.close()


# Diese Fixture wird vor JEDEM Test ausgeführt (`scope="function"`)
# und automatisch (`autouse=True`).
@pytest.fixture(scope="function", autouse=True)
def manage_test_db_data():
    """Pytest Function-Fixture: Bereitet die 'User'-Tabelle vor jedem Test vor.

    Diese Fixture stellt sicher, dass die Tabelle 'User' in der Test-Datenbank
    existiert und vor der Ausführung jedes Tests vollständig geleert wird (`TRUNCATE`).
    """
    print("\n--- Test-DB Setup (vor Test) ---")
    try:
        # Verwendung von 'with', um sicherzustellen, dass conn+cur geschlossen werden
        with get_test_db_connection() as conn:
            with conn.cursor() as cur:
                # Stellt sicher, dass die Tabelle existiert
                print("Sicherstellen, dass Tabelle 'User' existiert...")
                create_query = ('CREATE TABLE IF NOT EXISTS "User" ('
                                'username VARCHAR(100) PRIMARY KEY,'
                                'password VARCHAR(255) NOT NULL,'
                                'score INTEGER);')
                cur.execute(create_query)
                print("Tabelle 'User' bereit.")

                # Leert die Tabelle vor dem Test für einen sauberen Zustand
                # RESTART IDENTITY setzt Sequenzen zurück
                print("Leere Tabelle 'User'...")
                clear_query = 'TRUNCATE TABLE "User" RESTART IDENTITY;'
                cur.execute(clear_query)
                print("Tabelle 'User' geleert.")

        # yield markiert den Punkt, an dem der Test ausgeführt wird
        yield

    except Exception as e:
        print(f"FEHLER während des Test-DB Setups: {e}")
        # Fehler weiterleiten, damit der Test fehlschlägt
        raise
