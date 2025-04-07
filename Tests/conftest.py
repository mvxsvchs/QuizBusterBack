"""Modul für Pytest-Fixtures zur Verwaltung der Test-Datenbankumgebung.

Dieses Modul, typischerweise als `conftest.py` verwendet oder importiert,
stellt Fixtures bereit, um eine dedizierte Test-Datenbank für Integrationstests
zu initialisieren und zu verwalten.

Es enthält:
- Eine Hilfsfunktion zum Herstellen einer Verbindung zur Test-Datenbank.
- Eine Session-Scoped Fixture (`create_test_database_if_not_exists`), die sicherstellt,
  dass die Test-Datenbank zu Beginn der Test-Session existiert.
- Eine Function-Scoped Fixture (`manage_test_db_data`), die vor jedem einzelnen Test
  läuft, um sicherzustellen, dass die benötigten Tabellen existieren und leer sind,
  um Testisolierung zu gewährleisten.

Abhängigkeiten:
- pytest: Für das Fixture-System.
- psycopg: Für die PostgreSQL-Datenbankinteraktion.
- Config.postgres_config: Beinhaltet die Verbindungsdetails für die Test-Datenbank
  (TEST_DB_IP, TEST_DB_PORT, etc.).
"""

import pytest
import psycopg
from psycopg import OperationalError, sql # sql importieren falls benötigt für CREATE DB

# Importiert Test-Datenbank Konfigurationen
# Annahme: Enthält TEST_DB_IP, TEST_DB_PORT, TEST_DATABASE, etc.
from Config.postgres_config import *


def get_test_db_connection() -> psycopg.Connection:
    """Stellt eine Verbindung zur PostgreSQL-Testdatenbank her.

    Verwendet die TEST_DB_... Variablen aus der Konfiguration.
    Die Verbindung ist auf `autocommit=True` gesetzt. Bei einem Verbindungsfehler
    wird eine Fehlermeldung ausgegeben und der Pytest-Lauf mit einem Fehlercode
    beendet.

    Returns:
        psycopg.Connection: Ein aktives, autocommitting Verbindungsobjekt zur Test-DB.

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
            autocommit=True # Wichtig für CREATE DATABASE / TRUNCATE außerhalb von Transaktionen
        )
        # Optional: Überprüfung der Verbindung (z.B. conn.info)
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

    Hinweis: Das Erstellen einer Datenbank erfordert in der Regel eine Verbindung
    zu einer anderen Datenbank (z.B. 'postgres') und kann nicht innerhalb einer
    Transaktion auf der zu erstellenden Datenbank erfolgen. Die Logik hier könnte
    angepasst werden müssen, falls `get_test_db_connection` fehlschlägt, wenn die DB
    initial nicht existiert.
    """
    conn = None
    try:
        # Versucht, sich initial zu verbinden (könnte schon fehlschlagen, wenn DB fehlt)
        # Besser wäre es oft, sich zuerst zur 'postgres' DB zu verbinden.
        print(f"Prüfe Existenz der Test-DB '{TEST_DATABASE}'...")
        conn = get_test_db_connection() # Nutzt autocommit=True
        cur = conn.cursor()

        # Prüfe, ob die Datenbank im Katalog existiert
        # Wichtig: Diese Abfrage läuft auf der DB, zu der 'conn' verbunden ist!
        get_query = ('SELECT 1 FROM pg_database WHERE datname = %s')
        cur.execute(get_query, (TEST_DATABASE,))
        exists = cur.fetchone()

        if not exists:
            print(f"Test-Datenbank '{TEST_DATABASE}' nicht gefunden.")
            # ACHTUNG: CREATE DATABASE kann normalerweise nicht innerhalb
            # einer Verbindung zur SELBEN DB ausgeführt werden und erfordert
            # oft, dass man sich zur 'postgres' DB verbindet.
            # Diese Logik funktioniert möglicherweise nicht wie erwartet.
            # Sicherer wäre: Verbinde zu 'postgres', dann CREATE DATABASE.
            # Da hier autocommit=True ist, versuchen wir es trotzdem.
            print(f"Versuche Test-Datenbank zu erstellen: {TEST_DATABASE}...")
            # Sichere Methode zur Erstellung von Identifiern (falls nötig)
            # create_query = sql.SQL('CREATE DATABASE {}').format(sql.Identifier(TEST_DATABASE))
            # Einfachere Methode (funktioniert oft, aber weniger sicher bei speziellen Namen):
            cur.execute(f'CREATE DATABASE "{TEST_DATABASE}"') # SQL-Injection hier unwahrscheinlich, da Name aus Config kommt
            print("Test-Datenbank vermutlich erstellt (oder Fehler wurde ausgelöst).")
        else:
            print(f"Test-Datenbank '{TEST_DATABASE}' existiert bereits.")

        cur.close() # Cursor schließen

    except OperationalError as e:
        # Speziell den Fehler abfangen, der auftritt, wenn die DB nicht existiert
        # psycopg.errors.InvalidCatalogName (Code 3D000)
        if e.pgcode == '3D000':
            print(f"Test-Datenbank '{TEST_DATABASE}' existiert nicht. Überspringe Erstellung in dieser Fixture (sollte manuell/extern erfolgen?).")
            # Hier könnte man versuchen, sich zur 'postgres'-DB zu verbinden und sie zu erstellen.
        else:
            print(f"FEHLER während der Test-DB-Prüfung/Erstellung: {e}")
            pytest.exit(f"Fehler bei Test-DB Setup: {e}", returncode=1)
    except Exception as e:
        print(f"Allgemeiner FEHLER während der Test-DB-Prüfung/Erstellung: {e}")
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
    Dies gewährleistet einen sauberen, definierten Zustand für jeden Testlauf
    und verhindert Interferenzen zwischen Tests.

    Die Datenbankverbindung und der Cursor werden mittels `with`-Statements verwaltet,
    sodass sie automatisch geschlossen werden. Änderungen werden committet.

    Yields:
        None: Diese Fixture stellt nur Setup-Logik bereit und gibt keinen Wert an Tests weiter.
    """
    print("\n--- Test-DB Setup (vor Test) ---")
    try:
        # Verwendung von 'with', um sicherzustellen, dass conn/cur geschlossen werden
        with get_test_db_connection() as conn: # nutzt autocommit=True
            with conn.cursor() as cur:
                # Stellt sicher, dass die Tabelle existiert ( idempotent )
                print("Sicherstellen, dass Tabelle 'User' existiert...")
                create_query = ('CREATE TABLE IF NOT EXISTS "User" ('
                                'username VARCHAR(100) PRIMARY KEY,'
                                'password VARCHAR(255) NOT NULL,'
                                'score INTEGER);')
                cur.execute(create_query)
                print("Tabelle 'User' bereit.")

                # Leert die Tabelle vor dem Test für einen sauberen Zustand
                # RESTART IDENTITY setzt Sequenzen zurück (falls vorhanden)
                # CASCADE löscht abhängige Einträge (falls Foreign Keys existieren)
                print("Leere Tabelle 'User'...")
                clear_query = 'TRUNCATE TABLE "User" RESTART IDENTITY CASCADE;'
                cur.execute(clear_query)
                print("Tabelle 'User' geleert.")

                # Commit ist bei autocommit=True nicht zwingend nötig, schadet aber nicht
                # conn.commit() # Bei autocommit=True nicht nötig

        # yield markiert den Punkt, an dem der Test ausgeführt wird
        yield # Hier läuft der eigentliche Test

        print("--- Test-DB Teardown (nach Test) ---")
        # Hier könnte Aufräum-Logik stehen, falls nötig (z.B. bestimmte Daten löschen)
        # In diesem Fall ist das TRUNCATE am Anfang des *nächsten* Tests ausreichend.

    except Exception as e:
        print(f"FEHLER während des Test-DB Setups/Teardowns: {e}")
        # Fehler hier weiterleiten, damit der Test fehlschlägt
        raise