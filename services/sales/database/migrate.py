from pathlib import Path

from database.database import get_connection

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def run_migrations():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            IF OBJECT_ID('schema_migrations', 'U') IS NULL
            CREATE TABLE schema_migrations (
                version NVARCHAR(100) NOT NULL PRIMARY KEY,
                applied_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
            )
            """
        )
        connection.commit()

        cursor.execute("SELECT version FROM schema_migrations")
        applied = {row["version"] for row in cursor.fetchall()}

        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            version = path.stem
            if version in applied:
                continue

            print(f"Aplicando migración {version}...")
            cursor.execute(path.read_text(encoding="utf-8-sig"))
            cursor.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (version,))
            connection.commit()
            print(f"Migración {version} aplicada.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()