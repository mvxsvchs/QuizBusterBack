from Database.game_operations import get_category_list, get_question_list


def random_category_list(count: int) -> list:
    # Gibt eine liste von zufälligen Kategorien
    return get_category_list(count)


def random_question_list(category: int, count: int, ) -> list:
    # Gibt eine liste von zufälligen Fragen der gegebenen Kategorie
    return get_question_list(category, count)
