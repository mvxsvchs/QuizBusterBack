import psycopg
from Config.postgres_config import *


def get_connection():
    conn = psycopg.connect(
        host=ip,
        port=port,
        dbname=database,
        user=db_username,
        password=db_password
    )
    return conn
