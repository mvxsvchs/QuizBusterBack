import psycopg
from Config.postgres_config import *


# Verbindung zur Datenbank wird mit Daten aus config durchgeführt
def get_connection():
    conn = psycopg.connect(
        host=db_ip,
        port=db_port,
        dbname=database,
        user=db_username,
        password=db_password
    )
    return conn
