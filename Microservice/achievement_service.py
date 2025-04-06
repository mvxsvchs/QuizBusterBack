from pydantic import BaseModel

from Database.achievement_operations import get_achievement_list, get_user_achievement_list, add_user_achievement


# Klasse für das Nutzer Achievement JSON
class Achievement(BaseModel):
    id: int


def all_achievements() -> list[Achievement]:
    return get_achievement_list()


def user_achievements(username: str) -> list[Achievement]:
    return get_user_achievement_list(username=username)


def unlock_user_achievement(username: str, achievement: Achievement):
    return add_user_achievement(username=username, achievement_id=achievement.id)
