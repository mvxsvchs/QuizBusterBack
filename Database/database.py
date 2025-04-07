import psycopg
from Config.postgres_config import *


# Verbindung zur Datenbank wird mit Daten aus config durchgeführt
def get_connection():
    conn = psycopg.connect(
        host=DB_IP,
        port=DB_PORT,
        dbname=DATABASE,
        user=DB_USERNAME,
        password=DB_PASSWORD
    )
    return conn
