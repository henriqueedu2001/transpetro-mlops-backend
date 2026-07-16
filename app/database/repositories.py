from pathlib import Path
from datetime import datetime
from typing import *
from app.database.database_manager import Database
from app.modules.file_handler import *

class Repository:
    def __init__(self, db: Database):
        self.db = db 
    

    def create_training(
            self,
            file: bytes,
            train_name: str,
            project_name: str,
            project_owner: str,
            epochs: int,
            batch: int,
            workers: int
    ):
        # creates the training
        print(f'>>> train: {train_name}, {project_name}, {project_owner}')
        query = 'INSERT INTO train(train_name, project_name, project_owner) VALUES(%s, %s, %s)'
        self.db.execute(query, (train_name, project_name, project_owner))

        # fetches the train_id
        train_id = self.db.cursor.lastrowid

        # creates the params table
        print(f'>>> params: {train_id}, {epochs}, {batch}, {workers}')
        query = 'INSERT INTO params(id, epochs, batch, workers) VALUES(%s, %s, %s, %s)'
        self.db.execute(query, (train_id, epochs, batch, workers))

        # creates the job
        status = 'created'
        print(f'>>> job: {train_id}, {status}')
        query = 'INSERT INTO jobs(id, status) VALUES(%s, %s)'
        self.db.execute(query, (train_id, status))

        # create the folder
        file_type = 'dataset_dir'
        dataset_dir = str(get_dataset_dir(train_id, project_name))
        query = 'INSERT INTO files(train_id, file_type, file_path) VALUES(%s, %s, %s)'
        self.db.execute(query, (train_id, file_type, dataset_dir))

        # creates the file
        file_type = 'dataset_zip'
        dataset_path = str(get_dataset_path(file, train_id, project_name))
        query = 'INSERT INTO files(train_id, file_type, file_path) VALUES(%s, %s, %s)'
        self.db.execute(query, (train_id, file_type, dataset_path))

        self.db.commit()

        return train_id, dataset_path
    

