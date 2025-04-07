"""Testmodul für den `/user/score` API-Endpunkt.

Dieses Modul enthält Integrationstests für den PATCH-Endpunkt `/user/score`,
der zum Aktualisieren des Punktestands eines Benutzers dient.

Es verwendet `pytest` und `fastapi.testclient.TestClient`, um HTTP-Anfragen
an die FastAPI-Anwendung zu simulieren. Es beinhaltet auch Hilfsfunktionen
zum Einrichten von Testdaten (Benutzer in der Test-DB erstellen, Tokens generieren)
und zum Überprüfen des Datenbankzustands nach dem Test.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Optional

from Microservice.user_service import create_access_token
from Tests.conftest import get_test_db_connection
from main import app
from Database.user_operations import UserModel


# region ↓ Pytest Fixtures ↓

@pytest.fixture(scope="module")
def test_client():
    """Pytest Module-Fixture: Stellt einen TestClient für die FastAPI-App bereit.

    Dieser Client ermöglicht das Senden von simulierten HTTP-Anfragen an die
    FastAPI-Anwendung (`main.app`), ohne einen tatsächlichen Server starten
    zu müssen.

    Yields:
        TestClient: Eine Instanz von `fastapi.testclient.TestClient`.
    """
    # Erstellt den TestClient mit der FastAPI-App-Instanz
    client = TestClient(app)
    # Gibt den Client an die Tests weiter
    yield client


# endregion

# region ↓ Hilfsfunktionen ↓

def insert_user_with_score(username: str, initial_score: int) -> None:
    """Hilfsfunktion zum Einfügen eines Testbenutzers mit Score in die Test-DB.

    Verbindet sich zur Test-Datenbank und fügt einen Benutzer mit dem
    angegebenen Benutzernamen, einem festen Dummy-Passwort und dem
    initialen Score ein.

    Args:
        username (str): Der Benutzername des zu erstellenden Testbenutzers.
        initial_score (int): Der initiale Punktestand für den Testbenutzer.

    Raises:
        Exception: Leitet Datenbankfehler weiter, die beim Einfügen auftreten.
    """
    # Definiert ein festes Passwort nur für Testzwecke
    dummy_password = "test_password_123"
    print(
        f"Versuche, Benutzer '{username}' mit Score {initial_score} einzufügen"
    )
    try:
        with get_test_db_connection() as conn:
            with conn.cursor() as cur:
                # SQL-Befehl zum Einfügen
                insert_query = ('INSERT INTO "User" (username, password, score)'
                                ' VALUES (%s, %s, %s)')
                # Führt den Befehl mit Parametern aus
                cur.execute(insert_query, (username, dummy_password, initial_score))
                print(f"Benutzer '{username}' erfolgreich eingefügt.")
    except Exception as e:
        print(f"FEHLER beim Einfügen von Benutzer '{username}': {e}")
        raise  # Fehler weiterleiten, damit der Test fehlschlägt


def create_test_token(username: str) -> str:
    """Hilfsfunktion zum Erstellen eines gültigen JWT für einen Testbenutzer.

    Args:
        username (str): Der Benutzername, für den das Token erstellt werden soll.

    Returns:
        str: Der generierte JWT Access Token als String.
    """
    print(f"Erstelle Token für Nutzer '{username}'")
    # Ruft die eigentliche Token-Erstellungsfunktion auf
    return create_access_token(data={"sub": username})


def get_user_score_from_db(username: str) -> Optional[int]:
    """Hilfsfunktion zum Abrufen des Scores eines Benutzers direkt aus der Test-DB.

    Verbindet sich zur Test-Datenbank, fragt den Score für den gegebenen
    Benutzernamen ab und gibt ihn zurück.

    Args:
        username (str): Der Benutzername, dessen Score abgefragt werden soll.

    Returns:
        Optional[int]: Der Score des Benutzers als Integer, oder None, wenn der
                       Benutzer nicht gefunden wurde oder ein Fehler auftrat.
    """
    conn = None
    try:
        # Holt eine Verbindung zur Test-DB
        conn = get_test_db_connection()
        cur = conn.cursor()
        # SQL-Abfrage für den Score
        get_query = 'SELECT "score" FROM "User" WHERE "username" = %s'
        cur.execute(get_query, (username,))
        result = cur.fetchone()

        # Extrahiert den Score aus dem Ergebnis-Tupel
        score = result[0] if result else None
        return score
    except Exception as e:
        print(f"FEHLER beim Abrufen des Scores für '{username}': {e}")
        # Gibt None im Fehlerfall zurück
        return None
    finally:
        # Schließt die Verbindung, falls sie geöffnet wurde
        if conn and not conn.closed:
            conn.close()


# endregion

# region ↓ Tests ↓

def test_patch_score_success(test_client: TestClient, mocker, create_test_database_if_not_exists, manage_test_db_data):
    """Testet den Erfolgsfall für den PATCH /user/score Endpunkt.

    Szenario:
    - Ein Benutzer existiert in der Test-Datenbank mit einem initialen Score.
    - Ein gültiges JWT für diesen Benutzer wird bereitgestellt.
    - Eine Anfrage zum Hinzufügen von Punkten wird gesendet.
    Erwartetes Ergebnis:
    - Der Endpunkt antwortet mit Status 200 OK.
    - Die Antwort enthält den korrekt berechneten neuen Gesamtscore.
    - Der Score des Benutzers in der Datenbank wird korrekt aktualisiert.

    Args:
        test_client (TestClient): Der FastAPI TestClient.
        mocker: Der Mock.
    """
    # GIVEN: Testdaten und Ausgangszustand
    test_username = "score_user"
    initial_score = 100
    points_to_add = 25
    expected_final_score = initial_score + points_to_add

    # Benutzer in Test-DB erstellen
    insert_user_with_score(test_username, initial_score)
    # Gültigen Token für den Benutzer erstellen
    valid_token = create_test_token(test_username)
    # Authentifizierungs-Header vorbereiten
    headers = {"Authorization": f"Bearer {valid_token}"}
    # Request Body für die Patch-Anfrage definieren
    request_body = {"points": points_to_add}

    # Abhängigkeiten mocken, die im API-Call verwendet werden
    # Stelle sicher, dass Operationen innerhalb des API-Calls die Test-DB nutzen
    mock_conn = get_test_db_connection()
    mocker.patch(
        'Database.user_operations.get_connection',
        return_value=mock_conn
    )
    # Mocke auch get_user in main.py, da verify_user_token es verwendet
    # Wichtig: Das Passwort hier ist irrelevant, da verify_password nicht getestet wird.
    mocker.patch(
        'main.get_user',
        return_value=UserModel(username=test_username, password="dummy_hash", score=initial_score)
    )

    # WHEN: Die PATCH-Anfrage an den Endpunkt gesendet wird
    response = test_client.patch("/user/score", json=request_body, headers=headers)

    # THEN: Überprüfe die Antwort der API
    # Status Code sollte 200 OK sein
    assert response.status_code == 200, f"Erwartet Status 200, erhielt {response.status_code}"
    # Der Response Body sollte den neuen, korrekten Score enthalten
    assert response.json() == {"points": expected_final_score}, \
        f"Erwartet Body {{'points': {expected_final_score}}}, erhielt {response.json()}"

    # AND: Überprüfe den Zustand in der Datenbank
    db_score = get_user_score_from_db(test_username)
    assert db_score == expected_final_score, \
        f"Erwartet Score {expected_final_score} in DB, fand {db_score}"

# endregion
