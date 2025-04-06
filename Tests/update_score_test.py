import pytest
from fastapi.testclient import TestClient
from pytest_mock import mocker

from Microservice.user_service import create_access_token
from Tests.conftest import get_test_db_connection
from main import app
from Database.user_operations import get_connection, UserModel


# region ↓ Pytest Fixtures ↓

@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    yield client


# endregion

# region ↓ Hilfsfunktionen ↓

# Fügt einen Testbenutzer mit einem initialen Score und einem Dummy-Passwort in die Test-Datenbank ein
def insert_user_with_score(username: str, initial_score: int):
    dummy_password = "test_password_123"
    print(
        f"Versuche, Benutzer '{username}' mit Score {initial_score} und Dummy-Passwort einzufügen")

    conn = None
    try:
        # Verwendet die Test-DB-Verbindung
        with get_test_db_connection() as conn:
            # 'with' stellt sicher, dass cur.close() aufgerufen wird
            with conn.cursor() as cur:
                insert_query = ('INSERT INTO "User" (username, password, score)'
                                ' VALUES (%s, %s, %s)')

                cur.execute(insert_query, (username, dummy_password, initial_score))
                conn.commit()
                print(f"Benutzer '{username}' erfolgreich eingefügt")
    except Exception as e:
        print(f"Fehler beim Einfügen von Benutzer '{username}': {e}")
        if conn:
            conn.rollback()
        raise


# Erstellt einen gültigen JWT für einen Testbenutzer
def create_test_token(username: str) -> str:
    print(f"Erstelle Token für Nutzer {username}")
    return create_access_token(data={"sub": username})


# Holt den aktuellen Score eines Benutzers aus der Test-DB
def get_user_score_from_db(username: str) -> int | None:
    print(f"Erhalte score für Nutzer {username}")
    try:
        conn = get_test_db_connection()
        cur = conn.cursor()
        get_query = ('SELECT "score" '
                     'FROM "User" '
                     'WHERE "username" = %s')
        cur.execute(get_query, (username,))
        result = cur.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Fehler beim Abrufen des Scores für Benutzer '{username}': {e}")
        return None


# endregion

# region ↓ Tests ↓

def test_patch_score_success(test_client, mocker):
    # GIVEN: Ein Benutzer in der Test-DB und ein gültiger Token
    test_username = "testuser"
    initial_score = 100
    points_to_add = 25
    expected_final_score = initial_score + points_to_add

    insert_user_with_score(test_username, initial_score)
    valid_token = create_test_token(test_username)
    headers = {"Authorization": f"Bearer {valid_token}"}
    request_body = {"points": points_to_add}

    # Ersetzt die normale DB-Verbindung durch die Test-DB-Verbindung
    mock_conn = get_test_db_connection()  # Hole Test-Verbindung
    mocker.patch(
        'Database.user_operations.get_connection',
        return_value=mock_conn
    )
    mocker.patch(
        'main.get_user',
        return_value=UserModel(username=test_username, password="maxi", score=initial_score)
    )

    # WHEN: Die PATCH-Anfrage an den Endpunkt gesendet wird
    response = test_client.patch("/user/score", json=request_body, headers=headers)

    # THEN: Die Antwort sollte 200 OK sein und den neuen Score enthalten
    assert response.status_code == 200
    assert response.json() == {"points": expected_final_score}

    # AND: Der Score in der Datenbank sollte aktualisiert sein
    db_score = get_user_score_from_db(test_username)
    assert db_score == expected_final_score

# endregion
