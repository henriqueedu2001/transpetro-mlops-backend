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
    """Clears all data from the tables created by the counterpart script.
    """
    log_message("Trying to connect to the MySQL Database...")
    try:
        with mysql.connector.connect(**DB_CONFIG) as conn:
            log_message('Connection with the MySQL Database was successful!')
            with conn.cursor() as cursor:
                try:
                    # Disable foreign key checks to allow truncation in any order
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                    log_message('Foreign key checks disabled')

                    # Truncate all tables (order does not matter now)
                    clear_jobs_table(cursor)
                    clear_files_table(cursor)
                    clear_params_table(cursor)
                    clear_train_table(cursor)

                    # Re-enable foreign key checks
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                    log_message('Foreign key checks re-enabled')

                    conn.commit()
                except Exception as error:
                    log_message(f'Error: {error}')
                    conn.rollback()
                finally:
                    conn.close()
    except Exception as error:
        log_message(f'Error: {error}')
    finally:
        # cursor is closed automatically by the context manager
        log_message('Connection closed')
    log_message('Application finished')
    return


def clear_train_table(cursor: MySQLCursor):
    clear_train_table_query = "TRUNCATE TABLE train;"
    clear_table('train', query=clear_train_table_query, cursor=cursor)
    return


def clear_params_table(cursor: MySQLCursor):
    clear_params_table_query = "TRUNCATE TABLE params;"
    clear_table('params', query=clear_params_table_query, cursor=cursor)
    return


def clear_files_table(cursor: MySQLCursor):
    clear_files_table_query = "TRUNCATE TABLE files;"
    clear_table('files', query=clear_files_table_query, cursor=cursor)
    return


def clear_jobs_table(cursor: MySQLCursor):
    clear_jobs_table_query = "TRUNCATE TABLE jobs;"
    clear_table('jobs', query=clear_jobs_table_query, cursor=cursor)
    return


def clear_table(table_name: str, query: str, cursor: MySQLCursor):
    try:
        log_message(f'Clearing table \"{table_name}\"')
        cursor.execute(query)
        log_message(f'Table \"{table_name}\" cleared with success!')
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