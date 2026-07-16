import mysql.connector
from typing import *
from datetime import datetime
from collections.abc import Callable
from mysql.connector.cursor import MySQLCursor
from mysql.connector import MySQLConnection

DB_CONFIG = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'admin123',
    'database': 'transpetro',
    'port': '5470'
}

def main():
    """Drops all tables created by the counterpart script.
    """
    log_message("Trying to connect to the MySQL Database...")
    try:
        with mysql.connector.connect(**DB_CONFIG) as conn:
            log_message('Connection with the MySQL Database was successful!')
            with conn.cursor() as cursor:
                try:
                    # Drop tables in reverse order of creation to respect foreign keys
                    drop_jobs_table(cursor)
                    drop_files_table(cursor)
                    drop_params_table(cursor)
                    drop_train_table(cursor)
                except Exception as error:
                    log_message(f'Error: {error}')
                    conn.rollback()
                finally:
                    conn.close()
    except Exception as error:
        log_message(f'Error: {error}')
    finally:
        # cursor is closed automatically by the context manager, but we log
        log_message('Connection closed')
    log_message('Application finished')
    return


def drop_train_table(cursor: MySQLCursor):
    drop_train_table_query = "DROP TABLE IF EXISTS train;"
    drop_table('train', query=drop_train_table_query, cursor=cursor)
    return


def drop_params_table(cursor: MySQLCursor):
    drop_params_table_query = "DROP TABLE IF EXISTS params;"
    drop_table('params', query=drop_params_table_query, cursor=cursor)
    return


def drop_files_table(cursor: MySQLCursor):
    drop_files_table_query = "DROP TABLE IF EXISTS files;"
    drop_table('files', query=drop_files_table_query, cursor=cursor)
    return


def drop_jobs_table(cursor: MySQLCursor):
    drop_jobs_table_query = "DROP TABLE IF EXISTS jobs;"
    drop_table('jobs', query=drop_jobs_table_query, cursor=cursor)
    return


def drop_table(table_name: str, query: str, cursor: MySQLCursor):
    try:
        log_message(f'Dropping table \"{table_name}\"')
        cursor.execute(query)
        log_message(f'Table \"{table_name}\" dropped with success!')
    except Exception as error:
        raise error
    return


def log_message(message: str):
    """Logs the message, by printing it with the current timestamp.

    Args:
        message (str): the log message
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")


if __name__ == "__main__":
    main()