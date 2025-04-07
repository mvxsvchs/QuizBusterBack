"""Service-Modul für Achievement-bezogene Operationen.

Dieses Modul dient als Schnittstelle oder Service-Schicht für Aktionen,
die Achievements betreffen. Es definiert ein Modell `Achievement`
für die API-Anfragen und ruft entsprechende Funktionen aus dem Datenbank-Modul auf,
um Achievements abzurufen oder einem Benutzer zuzuweisen.
"""

from pydantic import BaseModel

from Database.achievement_operations import (
    get_achievement_list,
    get_user_achievement_list,
    add_user_achievement,
    AchievementModel,
)


# pylint: disable=too-few-public-methods
class Achievement(BaseModel):
    """Modell zur Repräsentation einer Achievement-Anfrage."""
    id: int


def all_achievements() -> list[AchievementModel]:
    """Ruft eine Liste aller im System definierten Achievements ab.

    Returns:
        list[AchievementModel]: Eine Liste von Achievement-Objekten, wie sie von der
                             Datenbank zurückgegeben werden
    """
    return get_achievement_list()


def user_achievements(username: str) -> list[AchievementModel]:
    """Ruft die Liste der Achievements ab, die ein bestimmter Benutzer erreicht hat.

    Args:
        username (str): Der Benutzername des Benutzers, dessen Achievements
                        abgerufen werden sollen.

    Returns:
        list[AchievementModel]: Eine Liste der Achievement-Objekte,
                             die der angegebene Benutzer freigeschaltet hat.
    """
    return get_user_achievement_list(username=username)


def unlock_user_achievement(username: str, achievement: Achievement) -> dict:
    """Schaltet ein Achievement für einen bestimmten Benutzer frei.

    Args:
        username (str): Der Benutzername des Benutzers.
        achievement (Achievement): Das API-Modell, das die `id` des
                                   freizuschaltenden Achievements enthält.

    Returns:
        dict: Das Ergebnis der `add_user_achievement`-Funktion,
              das den Erfolg
              (`{"message": "User achievement added."}`)
              oder das Vorhandensein des Eintrags
              (`{"message": "User achievement already exists."}`)
              anzeigt.
    """
    return add_user_achievement(username=username, achievement_id=achievement.id)
