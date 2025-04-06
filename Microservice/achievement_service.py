from pydantic import BaseModel

from Database.achievement_operations import get_achievement_list, get_user_achievement_list, Achievement, \
    add_user_achievement


def all_achievements() -> list[Achievement]:
    return get_achievement_list()


def user_achievements(username: str) -> list[Achievement]:
    return get_user_achievement_list(username=username)


def unlock_user_achievement(username: str, achievement_id: int):
    return add_user_achievement(username=username, achievement_id=achievement_id)
