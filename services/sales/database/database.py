import os
import time
from urllib.parse import unquote, urlsplit

import pymssql

DB_CONNECT_RETRIES = int(os.getenv("DB_CONNECT_RETRIES", "5"))
DB_RETRY_DELAY_S = float(os.getenv("DB_RETRY_DELAY_S", "3"))


def _connection_settings():
    """Lee DATABASE_URL, por ejemplo mssql://user:password@host:1433/database"""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")

    parts = urlsplit(url)
    return {
        "server": parts.hostname,
        "port": parts.port or 1433,
        "user": unquote(parts.username or ""),
        "password": unquote(parts.password or ""),
        "database": parts.path.lstrip("/"),
    }


def get_connection(retries=DB_CONNECT_RETRIES):
    settings = _connection_settings()

    for attempt in range(1, retries + 1):
        try:
            return pymssql.connect(
                **settings,
                as_dict=True,
                login_timeout=10,
                timeout=30,
            )
        except pymssql.OperationalError:
            if attempt == retries:
                raise
            time.sleep(DB_RETRY_DELAY_S * attempt)