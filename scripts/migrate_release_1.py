"""Non-destructive database migration for Release 1."""

import os

import mysql.connector
from dotenv import load_dotenv


load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "admin123"),
    "database": os.getenv("DB_DATABASE", "transpetro"),
    "port": int(os.getenv("DB_PORT", "5470")),
}


def column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(
        """SELECT COUNT(*) AS count FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s""",
        (DB_CONFIG["database"], table, column),
    )
    return cursor.fetchone()[0] > 0


def add_column(cursor, table: str, column: str, definition: str) -> None:
    if not column_exists(cursor, table, column):
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def main() -> None:
    with mysql.connector.connect(**DB_CONFIG) as connection:
        with connection.cursor() as cursor:
            add_column(cursor, "params", "model_version", "VARCHAR(32) NOT NULL DEFAULT 'yolov8'")
            add_column(cursor, "params", "model_size", "VARCHAR(8) NOT NULL DEFAULT 'n'")
            add_column(cursor, "params", "config_json", "JSON NULL")
            add_column(cursor, "jobs", "cancel_requested", "BOOLEAN NOT NULL DEFAULT FALSE")
            add_column(cursor, "jobs", "error_message", "TEXT NULL")
            add_column(cursor, "jobs", "log_path", "VARCHAR(1024) NULL")
            add_column(cursor, "jobs", "retry_count", "INT NOT NULL DEFAULT 0")

            cursor.execute(
                """ALTER TABLE jobs MODIFY status
                   ENUM('created','processing','finished','queued','running','succeeded','failed','cancelled')
                   NOT NULL DEFAULT 'queued'"""
            )
            cursor.execute("UPDATE jobs SET status='queued' WHERE status='created'")
            cursor.execute(
                """UPDATE jobs SET status='failed', finished_at=NOW(),
                   error_message='Job interrompido durante a migração da Release 1'
                   WHERE status='processing'"""
            )
            cursor.execute("UPDATE jobs SET status='succeeded' WHERE status='finished'")
            cursor.execute(
                """ALTER TABLE jobs MODIFY status
                   ENUM('queued','running','succeeded','failed','cancelled')
                   NOT NULL DEFAULT 'queued'"""
            )
            cursor.execute(
                """UPDATE jobs SET status='failed', finished_at=NOW(),
                   error_message='Job legado interrompido durante a migração da Release 1'
                   WHERE status='running' AND log_path IS NULL"""
            )
        connection.commit()
    print("Migração da Release 1 aplicada com sucesso.")


if __name__ == "__main__":
    main()
