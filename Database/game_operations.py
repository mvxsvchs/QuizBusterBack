from Database.database import get_connection
import random


class Category:
    # Constructor
    def __init__(self, id, name):
        self.id = id
        self.name = name


def create_category(category_result: list) -> list[Category]:
    result = list[Category]()
    for row in category_result:
        result.append(Category(row[0], row[1]))
    return result


def get_category_list(count: int) -> list[Category]:
    conn = get_connection()
    cur = conn.cursor()

    get_query = 'SELECT "ID", "name" FROM "Category";'
    cur.execute(get_query)
    result = cur.fetchall()

    cur.close()
    conn.close()
    random_values = random.sample(result, count)
    return create_category(random_values)
