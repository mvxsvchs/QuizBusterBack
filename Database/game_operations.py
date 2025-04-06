from Database.database import get_connection
import random


# region ↓ Abfragen für "Kategorie" Objekt ↓

# Klasse für Kategorie wie in Datenbank
class Category:
    # Constructor
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


# Erstelle Kategorie Objekt aus Datenbank Satz
def create_category(category_result: list) -> list[Category]:
    result = list[Category]()
    for row in category_result:
        # Aus jedem Eintrag der Datenbank wird ein Objekt erstellt
        result.append(Category(id=int(row[0]), name=str(row[1])))
    return result


def get_category_list(count: int) -> list[Category]:
    try:
        conn = get_connection()
        cur = conn.cursor()

        # SQL Abfrage zum Erhalten aller Kategorien
        get_query = ('SELECT "ID", "name" '
                     'FROM "Category";')
        cur.execute(get_query)
        # Alle Datensätze werden abgerufen
        result = cur.fetchall()

        cur.close()
        conn.close()

        # Es werden zufällig gewählte Eintäge aus der Liste gegeben
        # Zufall gegeben durch random Algorithmus von Python
        random_values = random.sample(result, count)
        # Der Datensatz im Listen-Format wird zu Objekt gewandelt
        return create_category(random_values)
    except Exception as error:
        # Gibt eine Fehlermeldung aus und wirft den Fehler erneut
        print("Fehler bei der Kategorie Abfrage:", error)
        raise error


# endregion

# region ↓ Abfragen für "Frage" Objekt ↓

# Klasse für Frage wie in Datenbank
class Question:
    def __init__(self, category: str, question: str, correct_answer: str, incorrect_answers: list[str]):
        self.category = category
        self.question = question
        self.correct_answer = correct_answer
        self.incorrect_answers = incorrect_answers


# Erstelle Frage Objekt aus Datenbank Satz
def create_question(question_result: list) -> list[Question]:
    result = list[Question]()
    for row in question_result:
        # Aus jedem Eintrag der Datenbank wird ein Objekt erstellt
        result.append(
            Question(category=str(row[0]), question=str(row[1]), correct_answer=str(row[2]), incorrect_answers=row[3]))
    return result


def get_question_list(category: int, count: int) -> list:
    try:
        conn = get_connection()
        cur = conn.cursor()

        # SQL Abfrage zum Erhalten aller Fragen der Kategorie
        get_query = (
            'SELECT "Category"."name", "Question"."question_text", "Question"."correct_answer", "Question"."incorrect_answers" '
            'FROM "Question" JOIN "Category" ON "Category"."ID" = "Question"."category_id" '
            'WHERE "Question"."category_id" = %s;')
        cur.execute(get_query, (category,))
        # Alle Datensätze werden abgerufen
        result = cur.fetchall()

        cur.close()
        conn.close()

        # Es werden zufällig gewählte Eintäge aus der Liste gegeben
        # Zufall gegeben durch random Algorithmus von Python
        random_values = random.sample(result, count)
        # Der Datensatz im Listen-Format wird zu Objekt gewandelt
        return create_question(random_values)
    except Exception as error:
        # Gibt eine Fehlermeldung aus und wirft den Fehler erneut
        print("Fehler bei der Fragen Abfrage:", error)
        raise error

# endregion
