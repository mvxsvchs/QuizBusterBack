import psycopg
from psycopg import OperationalError
from Config.postgres_config import DB_IP, DB_PORT, DATABASE, DB_USERNAME, DB_PASSWORD


def get_connection():
    """Stellt eine Verbindung zur PostgreSQL-Datenbank her.

    Diese Funktion liest die notwendigen Verbindungsparameter (Host, Port,
    Datenbankname, Benutzername, Passwort) der config in dem Modul 'Config.postgres_config'
    und verwendet die 'psycopg' Bibliothek, um eine Verbindung aufzubauen.

    Returns:
        psycopg.Connection: Ein aktives Verbindungsobjekt zur PostgreSQL-Datenbank.

    Raises:
        psycopg.OperationalError: Wenn die Verbindung zur Datenbank fehlschlägt
                                   (z.B. falsche Anmeldedaten, Server nicht
                                   erreichbar, Datenbank existiert nicht).
        ImportError: Wenn das Konfigurationsmodul 'Config.postgres_config' oder
                     die benötigten Variablen darin nicht gefunden werden können.
        Exception: Andere unerwartete Fehler während des Verbindungsvorgangs.
    """
    try:
        conn = psycopg.connect(
            host=DB_IP,
            port=DB_PORT,
            dbname=DATABASE,
            user=DB_USERNAME,
            password=DB_PASSWORD
        )
        return conn
    except OperationalError as e:
        print(f"Datenbankverbindungsfehler: {e}")
        raise
    except ImportError as e:
        print(f"Fehler beim Importieren der Konfiguration: {e}")
        raise
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        raise
