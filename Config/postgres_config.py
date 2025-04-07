"""Konfigurationsmodul für Datenbankverbindungsdaten.

Dieses Modul zentralisiert die Konfigurationsparameter, die für den Aufbau von
Verbindungen zu PostgreSQL-Datenbanken benötigt werden. Es enthält separate
Einstellungen für die Haupt-Datenbank und eine Datenbank für integration Tests.

Konstanten für die Haupt-Datenbank:
    DB_USERNAME (str): Benutzername für die Haupt-Datenbank.
    DB_PASSWORD (str): Passwort für die Haupt-Datenbank.
    DB_IP (str): Hostname oder IP-Adresse des Haupt-Datenbankservers.
    DB_PORT (str): Port des Haupt-Datenbankservers.
    DATABASE (str): Name der Haupt-Datenbank.

Konstanten für die Test-Datenbank:
    TEST_DB_USERNAME (str): Benutzername für die Test-Datenbank.
    TEST_DB_PASSWORD (str): Passwort für die Test-Datenbank.
    TEST_DB_IP (str): Hostname oder IP-Adresse des Test-Datenbankservers.
    TEST_DB_PORT (str): Port des Test-Datenbankservers.
    TEST_DATABASE (str): Name der Test-Datenbank.
"""

# region ↓ Config für die Datenbank ↓

# Login Daten für Datenbank
DB_USERNAME = "postgres"
DB_PASSWORD = "admin"
# Adresse der Datenbank
DB_IP = "localhost"
DB_PORT = "5432"
# Name der Datenbank
DATABASE = "postgres"

# endregion

# region ↓ Config für die Test-Datenbank ↓

# Login Daten für Test Datenbank
TEST_DB_USERNAME = "postgres"
TEST_DB_PASSWORD = "admin"
# Adresse der Test Datenbank
TEST_DB_IP = "localhost"
TEST_DB_PORT = "5432"
# Name der Datenbank
TEST_DATABASE = "test_postgres"

# endregion
