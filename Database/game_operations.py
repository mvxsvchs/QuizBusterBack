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
    try:
        conn = get_connection()
        cur = conn.cursor()

        get_query = 'SELECT "ID", "name" FROM "Category";'
        cur.execute(get_query)
        result = cur.fetchall()

        cur.close()
        conn.close()
        random_values = random.sample(result, count)
        return create_category(random_values)
    except Exception as error:
        # Gibt eine Fehlermeldung aus und wirft den Fehler erneut
        print("Fehler bei der Kategorie Abfrage:", error)
        raise error

class Question:
    def __init__(self, category, question, correct_answer, incorrect_answers):
        self.category = category
        self.question = question
        self.correct_answer = correct_answer
        self.incorrect_answers = incorrect_answers


def create_question(question_result: list) -> list[Question]:
    result = list[Question]()
    for row in question_result:
        result.append(Question(row[0], row[1], row[2], row[3]))
    return result


def get_question_list(category: int, count: int) -> list:
    try:
        conn = get_connection()
        cur = conn.cursor()

        get_query = (
            'SELECT "Category"."name", "Question"."question_text", "Question"."correct_answer", "Question"."incorrect_answers" '
            'FROM "Question" JOIN "Category" ON "Category"."ID" = "Question"."category_id" '
            'WHERE "Question"."category_id" = %s;')
        cur.execute(get_query, (category,))
        result = cur.fetchall()

        cur.close()
        conn.close()
        random_values = random.sample(result, count)
        return create_question(random_values)
    except Exception as error:
        # Gibt eine Fehlermeldung aus und wirft den Fehler erneut
        print("Fehler bei der Fragen Abfrage:", error)
        raise error
