from Database.game_operations import get_category_list, get_question_list


def random_category_list(count: int) -> list:
    return get_category_list(count)


def random_question_list(category: int, count: int, ) -> list:
    return get_question_list(category, count)
