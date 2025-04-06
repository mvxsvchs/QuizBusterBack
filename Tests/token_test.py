import unittest
import pytest
from fastapi import HTTPException
from jwt import InvalidTokenError

from Microservice.user_service import User
from main import verify_user_token


# Testet, ob verify_user_token eine 401 HTTPException auslöst,
# wenn jwt.decode eine InvalidTokenError wirft
@pytest.mark.asyncio
async def test_verify_user_token_decode_fails(mocker):
    # GIVEN: jwt.decode wird gemockt, um InvalidTokenError auszulösen
    mocker.patch('main.jwt.decode',
                 side_effect=InvalidTokenError("Simulierter Decode-Fehler"))

    # WHEN: Wir versuchen, verify_user_token mit einem beliebigen Token aufzurufen
    with pytest.raises(HTTPException) as exc_info:
        await verify_user_token("ein-ungueltiger-oder-dummy-token")

    # THEN: Wir erwarten eine HTTPException mit Statuscode 401
    assert exc_info.value.status_code == 401


# Testet, ob verify_user_token eine 401 HTTPException auslöst,
# wenn das dekodierte JWT Token keinen Benutzernamen enthält
@pytest.mark.asyncio
async def test_verify_user_token_payload_missing_username(mocker):
    # GIVEN: Ein JWT Token ohne Benutzername ('sub' fehlt im Payload)
    valid_payload_without_username = {
        "exp": 1678886400  # Ein Ablaufdatum
    }
    # AND: jwt.decode wird gemockt, sodass es ein gültiges Payload ohne 'sub' zurückgibt.
    mocker.patch(
        'main.jwt.decode',
        return_value=valid_payload_without_username
    )

    # WHEN: Wir versuchen, verify_user_token mit einem beliebigen Token aufzurufen
    with pytest.raises(HTTPException) as exc_info:
        await verify_user_token("ein_token_string_der_dekodiert_wird")

    # THEN: Wir erwarten eine HTTPException mit Statuscode 401
    assert exc_info.value.status_code == 401


#  Testet, ob verify_user_token eine 401 HTTPException auslöst,
#  wenn der Token gültig ist und einen Benutzernamen enthält,
#  dieser Benutzer aber nicht in der Datenbank existiert (get_user gibt None zurück)
@pytest.mark.asyncio
async def test_verify_user_token_user_not_found_in_db(mocker):
    # GIVEN: Ein korrekt formatierter JWT Token mit einem Benutzernamen
    username_from_token = "testuser"
    correct_payload = {
        "sub": username_from_token,
        "exp": 1678886400  # Ein Ablaufdatum
    }
    # AND: Die decode Funktion gibt den korrekten JWT Token zurück
    mocker.patch(
        'main.jwt.decode',
        return_value=correct_payload
    )

    # AND: Der Benutzer existiert nicht in unserer Datenbank
    mock_get_user = mocker.patch(
        'main.get_user',
        return_value=None
    )

    # WHEN: Wir versuchen, den Token zu verifizieren
    with pytest.raises(HTTPException) as exc_info:
        await verify_user_token("valid_token_for_unknown_user")

    # THEN: Wir erwarten eine HTTPException mit Statuscode 401
    assert exc_info.value.status_code == 401

    # AND: Wir erwarten, dass get_user mit dem korrekten Benutzernamen aus dem Payload aufgerufen wurde
    mock_get_user.assert_called_once_with(username=username_from_token)


# Testet den Erfolgsfall für verify_user_token
# - Token ist gültig und dekodierbar
# - Payload enthält einen Benutzernamen ('sub')
# - Benutzer existiert in der Datenbank (get_user gibt ein User-Objekt zurück)
@pytest.mark.asyncio
async def test_verify_user_token_success(mocker):
    # GIVEN: Ein korrekt formatierter JWT Token mit einem Benutzernamen
    username_from_token = "testuser"
    correct_payload = {
        "sub": username_from_token,
        "exp": 1678886400  # Ein Ablaufdatum
    }
    # AND: Die decode Funktion gibt den korrekten JWT Token zurück
    mocker.patch(
        'main.jwt.decode',
        return_value=correct_payload
    )

    # AND: Ein Benutzer mit dem gleichen username wie im Token
    mock_user_object = User(username=username_from_token, password="password")
    #  AND: Die get_user Funktion gibt den korrekten user zurück
    mock_get_user = mocker.patch(
        'main.get_user',
        return_value=mock_user_object
    )

    # WHEN: Wir versuchen, den Token zu verifizieren
    try:
        returned_user = await verify_user_token("valid_token_for_existing_user")
        # THEN: Wir erhalten das User-Objekt zurück, das von get_user zurückgegeben wurde
        assert returned_user is mock_user_object
    except HTTPException as e:
        # Wenn unerwartet eine HTTPException auftritt, lasse den Test fehlschlagen
        pytest.fail(f"verify_user_token raised HTTPException unexpectedly: {e}")

    # Stelle sicher, dass get_user mit dem korrekten Benutzernamen aufgerufen wurde
    mock_get_user.assert_called_once_with(username=username_from_token)
