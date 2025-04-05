from Database.database import get_connection
import random


def get_category_list(count: int) -> list:
    conn = get_connection()
    cur = conn.cursor()

    get_query = 'SELECT * FROM "Category";'
    cur.execute(get_query)
    result = cur.fetchall()

    cur.close()
    conn.close()
    return random.sample(result, count)
