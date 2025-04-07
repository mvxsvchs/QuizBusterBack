"""Testmodul für den `/user/score` API-Endpunkt.

Dieses Modul enthält Integrationstests für den PATCH-Endpunkt `/user/score`,
der zum Aktualisieren des Punktestands eines Benutzers dient.

Es verwendet `pytest` und `fastapi.testclient.TestClient`, um HTTP-Anfragen
an die FastAPI-Anwendung zu simulieren. Es beinhaltet auch Hilfsfunktionen
zum Einrichten von Testdaten (Benutzer in der Test-DB erstellen, Tokens generieren)
und zum Überprüfen des Datenbankzustands nach dem Test. Abhängigkeiten werden
mittels `pytest-mock` (mocker) bei Bedarf isoliert.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Optional # Für Type Hint in get_user_score_from_db

# Importiert Funktionen und Modelle aus den Service- und Datenbank-Schichten
from Microservice.user_service import create_access_token
# Annahme: conftest.py oder ein ähnliches Modul stellt diese Funktion bereit
from Tests.conftest import get_test_db_connection
from main import app # Die FastAPI App-Instanz
# Annahme: UserModel ist in user_operations definiert
from Database.user_operations import UserModel


# region ↓ Pytest Fixtures ↓

@pytest.fixture(scope="module")
def test_client() -> TestClient:
    """Pytest Module-Fixture: Stellt einen TestClient für die FastAPI-App bereit.

    Dieser Client ermöglicht das Senden von simulierten HTTP-Anfragen an die
    FastAPI-Anwendung (`main.app`), ohne einen tatsächlichen Server starten
    zu müssen. Die Fixture hat den Scope "module", d.h. der Client wird
    einmal pro Testmodul erstellt.

    Yields:
        TestClient: Eine Instanz von `fastapi.testclient.TestClient`.
    """
    # Erstellt den TestClient mit der FastAPI-App-Instanz
    client = TestClient(app)
    # Gibt den Client an die Tests weiter
    yield client
    # Hier könnte Aufräumcode stehen, falls nötig (nach allen Tests im Modul)


# endregion

# region ↓ Hilfsfunktionen ↓

def insert_user_with_score(username: str, initial_score: int) -> None:
    """Hilfsfunktion zum Einfügen eines Testbenutzers mit Score in die Test-DB.

    Verbindet sich zur Test-Datenbank und fügt einen Benutzer mit dem
    angegebenen Benutzernamen, einem festen Dummy-Passwort und dem
    initialen Score ein. Löst bei Fehlern eine Exception aus.

    Args:
        username (str): Der Benutzername des zu erstellenden Testbenutzers.
        initial_score (int): Der initiale Punktestand für den Testbenutzer.

    Raises:
        Exception: Leitet Datenbankfehler weiter, die beim Einfügen auftreten.
    """
    # Definiert ein festes Passwort nur für Testzwecke
    dummy_password = "test_password_123"
    print(
        f"\n[TEST SETUP] Versuche, Benutzer '{username}' mit Score {initial_score} einzufügen..."
    )

    conn = None
    try:
        # Verwendet die Test-DB-Verbindung innerhalb eines Context Managers
        with get_test_db_connection() as conn:
            # Stellt sicher, dass der Cursor automatisch geschlossen wird
            with conn.cursor() as cur:
                # SQL-Befehl zum Einfügen
                insert_query = ('INSERT INTO "User" (username, password, score)'
                                ' VALUES (%s, %s, %s)')
                # Führt den Befehl mit Parametern aus
                cur.execute(insert_query, (username, dummy_password, initial_score))
                # Commit ist bei autocommit=True der Test-Verbindung nicht nötig,
                # aber schadet hier auch nicht, falls autocommit entfernt wird.
                # conn.commit() # Bei autocommit=True nicht unbedingt erforderlich
                print(f"[TEST SETUP] Benutzer '{username}' erfolgreich eingefügt.")
    except Exception as e:
        print(f"[TEST SETUP] FEHLER beim Einfügen von Benutzer '{username}': {e}")
        # Optional: Rollback versuchen, falls kein autocommit
        # if conn:
        #     conn.rollback()
        raise # Fehler weiterleiten, damit der Test fehlschlägt


def create_test_token(username: str) -> str:
    """Hilfsfunktion zum Erstellen eines gültigen JWT für einen Testbenutzer.

    Wrapper um die `create_access_token`-Funktion aus dem user_service.

    Args:
        username (str): Der Benutzername, für den das Token erstellt werden soll
                        (dieser wird in den 'sub'-Claim des Tokens geschrieben).

    Returns:
        str: Der generierte JWT Access Token als String.
    """
    print(f"[TEST HELPER] Erstelle Token für Nutzer '{username}'")
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
    print(f"[TEST HELPER] Frage Score für Nutzer '{username}' aus DB ab...")
    conn = None
    score = None
    try:
        # Holt eine Verbindung zur Test-DB
        conn = get_test_db_connection()
        cur = conn.cursor()
        # SQL-Abfrage für den Score
        get_query = 'SELECT "score" FROM "User" WHERE "username" = %s'
        cur.execute(get_query, (username,))
        # Holt das Ergebnis (eine Zeile erwartet)
        result = cur.fetchone()
        # Extrahiert den Score aus dem Ergebnis-Tupel
        score = result[0] if result else None
        print(f"[TEST HELPER] Score für '{username}': {score}")
    except Exception as e:
        print(f"[TEST HELPER] FEHLER beim Abrufen des Scores für '{username}': {e}")
        score = None # Gibt None im Fehlerfall zurück
    finally:
        # Schließt die Verbindung, falls sie geöffnet wurde
        if conn and not conn.closed:
            conn.close()
    return score


# endregion

# region ↓ Tests ↓

def test_patch_score_success(test_client: TestClient, mocker):
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
        test_client (TestClient): Die Fixture für den FastAPI TestClient.
        mocker: Die Pytest-Mock Fixture.
    """
    # GIVEN: Testdaten und Ausgangszustand
    test_username = "score_user"
    initial_score = 100
    points_to_add = 25
    expected_final_score = initial_score + points_to_add

    # 1. Benutzer in Test-DB erstellen
    insert_user_with_score(test_username, initial_score)
    # 2. Gültigen Token für den Benutzer erstellen
    valid_token = create_test_token(test_username)
    # 3. Authentifizierungs-Header vorbereiten
    headers = {"Authorization": f"Bearer {valid_token}"}
    # 4. Request Body für die Patch-Anfrage definieren
    request_body = {"points": points_to_add}

    # 5. Abhängigkeiten mocken, die im API-Call verwendet werden
    #    Stelle sicher, dass Operationen innerhalb des API-Calls die Test-DB nutzen
    #    (Obwohl die Test-DB-Fixtures dies bereits tun sollten, ist explizites Mocking
    #    von get_connection innerhalb des *user_operations*-Moduls oft sicherer).
    mock_conn = get_test_db_connection() # Hole eine Test-Verbindung explizit
    mocker.patch(
        'Database.user_operations.get_connection', # Mocke dort, wo es verwendet wird
        return_value=mock_conn
    )
    # Mocke auch get_user in main.py, da verify_user_token es verwendet
    # Wichtig: Das Passwort hier ist irrelevant, da verify_password nicht getestet wird.
    # Der Score wird verwendet, um sicherzustellen, dass der richtige User zurückkommt.
    mocker.patch(
        'main.get_user',
        return_value=UserModel(username=test_username, password="dummy_hash", score=initial_score)
    )

    # WHEN: Die PATCH-Anfrage an den Endpunkt gesendet wird
    print(f"\n[TEST ACTION] Sende PATCH /user/score für '{test_username}' "
          f"mit body={request_body}")
    response = test_client.patch("/user/score", json=request_body, headers=headers)
    print(f"[TEST ACTION] Antwort erhalten: Status={response.status_code}, Body={response.text}")

    # THEN: Überprüfe die Antwort der API
    # 1. Status Code sollte 200 OK sein
    assert response.status_code == 200, f"Erwartet Status 200, erhielt {response.status_code}"
    # 2. Der Response Body sollte den neuen, korrekten Score enthalten
    assert response.json() == {"points": expected_final_score}, \
        f"Erwartet Body {{'points': {expected_final_score}}}, erhielt {response.json()}"

    # AND: Überprüfe den Zustand in der Datenbank
    # 3. Der Score in der Datenbank sollte korrekt aktualisiert worden sein
    db_score = get_user_score_from_db(test_username)
    print(f"[TEST VERIFY] Score in DB für '{test_username}': {db_score}")
    assert db_score == expected_final_score, \
        f"Erwartet Score {expected_final_score} in DB, fand {db_score}"

# endregion