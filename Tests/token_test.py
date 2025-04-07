"""Testmodul für die `verify_user_token` Funktion.

Dieses Modul enthält Unit-Tests für die Funktion `verify_user_token`
aus `main.py`. Es verwendet `pytest`, um verschiedene Szenarien
der Token-Verifizierung zu testen (Fehlerfälle und Erfolgsfall).
"""
import pytest
from fastapi import HTTPException
from jwt import InvalidTokenError

from Microservice.user_service import User
from main import verify_user_token


# Testet, ob verify_user_token eine 401 HTTPException auslöst,
# wenn jwt.decode eine InvalidTokenError wirft.
@pytest.mark.asyncio
async def test_verify_user_token_decode_fails(mocker):
    """Testet Fehlerfall: Token-Dekodierung schlägt fehl."""
    # GIVEN: jwt.decode wird gemockt, um InvalidTokenError auszulösen
    mocker.patch('main.jwt.decode',
                 side_effect=InvalidTokenError("Simulierter Decode-Fehler"))
    # AND: Ein User-Objekt, das den Benutzer repräsentiert
    mock_user_object = User(username="test", password="hashed_password_example")
    # AND: main.get_user gibt dieses User-Objekt zurück
    mock_get_user = mocker.patch(
        'main.get_user',
        return_value=mock_user_object
    )

    # WHEN: verify_user_token wird mit einem beliebigen Token aufgerufen
    with pytest.raises(HTTPException) as exc_info:
        await verify_user_token("ein-ungueltiger-oder-dummy-token")

    # THEN: Eine HTTPException mit Status 401 wird erwartet
    assert exc_info.value.status_code == 401
    # AND: get_user wurde nicht aufgerufen
    mock_get_user.assert_not_called()


# Testet, ob verify_user_token eine 401 HTTPException auslöst,
# wenn das dekodierte JWT Token keinen Benutzernamen enthält.
@pytest.mark.asyncio
async def test_verify_user_token_payload_missing_username(mocker):
    """Testet Fehlerfall: Benutzername fehlt im Token."""
    # GIVEN: Ein Payload ohne 'sub'-Eintrag
    valid_payload_without_username = {
        "exp": 1678886400  # Beispiel-Ablaufdatum
    }
    # AND: jwt.decode gibt diesen Payload zurück
    mocker.patch(
        'main.jwt.decode',
        return_value=valid_payload_without_username
    )
    # AND: Ein User-Objekt, das den Benutzer repräsentiert
    mock_user_object = User(username="test", password="hashed_password_example")
    # AND: main.get_user gibt dieses User-Objekt zurück
    mock_get_user = mocker.patch(
        'main.get_user',
        return_value=mock_user_object
    )

    # WHEN: verify_user_token wird aufgerufen
    with pytest.raises(HTTPException) as exc_info:
        await verify_user_token("token_wird_dekodiert_ohne_sub")

    # THEN: Eine HTTPException mit Status 401 wird erwartet
    assert exc_info.value.status_code == 401
    # AND: get_user wurde nicht aufgerufen
    mock_get_user.assert_not_called()


# Testet, ob verify_user_token eine 401 HTTPException auslöst,
# wenn der Token gültig ist und einen Benutzernamen enthält,
# dieser Benutzer aber nicht in der Datenbank existiert.
@pytest.mark.asyncio
async def test_verify_user_token_user_not_found_in_db(mocker):
    """Testet Fehlerfall: Benutzer aus gültigem Token nicht in DB gefunden."""
    # GIVEN: Ein gültiger Payload mit Benutzername
    username_from_token = "testuser"
    correct_payload = {
        "sub": username_from_token,
        "exp": 1678886400  # Beispiel-Ablaufdatum
    }
    # AND: jwt.decode gibt diesen Payload zurück
    mocker.patch(
        'main.jwt.decode',
        return_value=correct_payload
    )
    # AND: main.get_user gibt None zurück (Benutzer nicht gefunden)
    mock_get_user = mocker.patch(
        'main.get_user',
        return_value=None
    )

    # WHEN: verify_user_token wird aufgerufen
    with pytest.raises(HTTPException) as exc_info:
        await verify_user_token("valid_token_for_unknown_user")

    # THEN: Eine HTTPException mit Status 401 wird erwartet
    assert exc_info.value.status_code == 401
    # AND: get_user wurde mit dem korrekten Benutzernamen aufgerufen
    mock_get_user.assert_called_once_with(username=username_from_token)


# Testet den Erfolgsfall für verify_user_token:
# - Token ist gültig und dekodierbar.
# - Payload enthält einen Benutzernamen ('sub').
# - Benutzer existiert in der Datenbank (get_user gibt ein User-Objekt zurück).
@pytest.mark.asyncio
async def test_verify_user_token_success(mocker):
    """Testet Erfolgsfall: Gültiges Token für existierenden Benutzer."""
    # GIVEN: Ein gültiger Payload mit Benutzername
    username_from_token = "testuser"
    correct_payload = {
        "sub": username_from_token,
        "exp": 1678886400  # Beispiel-Ablaufdatum
    }
    # AND: jwt.decode gibt diesen Payload zurück
    mocker.patch(
        'main.jwt.decode',
        return_value=correct_payload
    )
    # AND: Ein User-Objekt, das den Benutzer repräsentiert
    mock_user_object = User(username=username_from_token, password="hashed_password_example")
    # AND: main.get_user gibt dieses User-Objekt zurück
    mock_get_user = mocker.patch(
        'main.get_user',
        return_value=mock_user_object
    )

    # WHEN: verify_user_token wird aufgerufen
    returned_user = await verify_user_token("valid_token_for_existing_user")

    # THEN: Das zurückgegebene User-Objekt ist das vom Mock bereitgestellte
    assert returned_user is mock_user_object
    # AND: get_user wurde mit dem korrekten Benutzernamen aufgerufen
    mock_get_user.assert_called_once_with(username=username_from_token)
