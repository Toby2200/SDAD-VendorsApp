import os
import time
import pymssql

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "1433"))
DB_NAME = os.getenv("DB_NAME", "catalog_db")
DB_USER = os.getenv("DB_USER", "catalog_user")
DB_CONNECT_RETRIES = int(os.getenv("DB_CONNECT_RETRIES", "5"))
DB_RETRY_DELAY_S = float(os.getenv("DB_RETRY_DELAY_S", "3"))


def get_connection(retries=DB_CONNECT_RETRIES):

    password = os.getenv("DB_PASSWORD")
    if not password:
        raise RuntimeError("CATALOG_DB_PASSWORD environment variable is not set.")

    for attempt in range(1, retries + 1):
        try:
           return pymssql.connect(
                server=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=password,
                database=DB_NAME,
                as_dict=True,
                login_timeout=10,
                timeout=30,
            )
        except pymssql.OperationalError:
            if attempt == retries:
                raise
            time.sleep(DB_RETRY_DELAY_S)