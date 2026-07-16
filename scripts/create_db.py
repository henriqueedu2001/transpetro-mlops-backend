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
    """Runs the retrieval and storing routine with MySQL and external APIs.
    """
    log_message("Trying to connect to the MySQL Database...")
    try:
        with mysql.connector.connect(**DB_CONFIG) as conn:
            log_message('Connection with the MySQL Database was successful!')
            with conn.cursor() as cursor:
                try:
                    create_train_table(cursor)
                    create_params_table(cursor)
                    create_files_table(cursor)
                    create_jobs_table(cursor)
                except Exception as error:
                    log_message(f'Error: {error}')
                    conn.rollback()
                finally:
                    conn.close()
    except Exception as error:
        log_message(f'Error: {error}')
    finally:
        cursor.close()
        log_message('Connection closed')
    log_message('Application finished')
    return


def create_train_table(cursor: MySQLCursor):
    create_train_table_query = """
        CREATE TABLE IF NOT EXISTS train (
            id INT AUTO_INCREMENT PRIMARY KEY,
            train_name VARCHAR(255),
            project_name VARCHAR(255),
            project_owner VARCHAR(255),
            created_at TIMESTAMP
        );
    """
    create_table('train', query=create_train_table_query, cursor=cursor)
    return


def create_params_table(cursor: MySQLCursor):
    create_params_table_query = """
        CREATE TABLE IF NOT EXISTS params (
            id INT AUTO_INCREMENT PRIMARY KEY,
            epochs INT,
            batch INT,
            workers INT,
            FOREIGN KEY (id) REFERENCES train(id)
        );
    """
    create_table('params', query=create_params_table_query, cursor=cursor)
    return


def create_files_table(cursor: MySQLCursor):
    create_files_table_query = """
        CREATE TABLE IF NOT EXISTS files (
            id INT AUTO_INCREMENT PRIMARY KEY,
            train_id INT,
            file_type VARCHAR(255),
            file_path VARCHAR(255),
            FOREIGN KEY (train_id) REFERENCES train(id)
        );
    """
    create_table('files', query=create_files_table_query, cursor=cursor)
    return

def create_jobs_table(cursor: MySQLCursor):
        create_jobs_table_query = """
        CREATE TABLE IF NOT EXISTS jobs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            train_id INT,
            status ENUM('created', 'processing', 'finished', 'cancelled'),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            scheduled_at TIMESTAMP,
            finished_at TIMESTAMP,
            FOREIGN KEY (train_id) REFERENCES train(id)
        );
    """
        create_table('jobs', query=create_jobs_table_query, cursor=cursor)


def create_table(table_name: str, query: str, cursor: MySQLCursor):
    try:
        log_message(f'Creating table \"{table_name}\"')
        cursor.execute(query)
        log_message(f'Table \"{table_name}\" created with success!')
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