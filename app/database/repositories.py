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
    ) -> Tuple[int, Path]:
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
        query = 'INSERT INTO jobs(train_id, status) VALUES(%s, %s)'
        self.db.execute(query, (train_id, status))

        # create the folder
        file_type = 'train_dir'
        dataset_dir = str(get_dataset_dir(train_id, project_name))
        query = 'INSERT INTO files(train_id, file_type, file_path) VALUES(%s, %s, %s)'
        self.db.execute(query, (train_id, file_type, dataset_dir))

        # creates the file
        file_type = 'dataset_dir'
        dataset_path = get_dataset_zip_path(file, train_id, project_name)
        dataset_path = Path(dataset_path).with_suffix('')
        query = 'INSERT INTO files(train_id, file_type, file_path) VALUES(%s, %s, %s)'
        self.db.execute(query, (train_id, file_type, str(dataset_path)))

        # creates the file
        file_type = 'dataset_zip'
        dataset_path = get_dataset_zip_path(file, train_id, project_name)
        query = 'INSERT INTO files(train_id, file_type, file_path) VALUES(%s, %s, %s)'
        self.db.execute(query, (train_id, file_type, str(dataset_path)))

        self.db.commit()

        return train_id, dataset_path
    

    def get_jobs(self) -> List[Dict]:
        query = """
            SELECT train_id, status, jobs.created_at, scheduled_at, finished_at, train_name, project_name, project_owner
            FROM jobs
            INNER JOIN train ON jobs.train_id = train.id
        """
        self.db.execute(query)
        jobs = self.db.fetch_all()
        return jobs


    def start_job(self, job_id: int):
        query = """
            UPDATE jobs
            SET status='processing', scheduled_at=NOW()
            WHERE train_id = %s;
        """

        self.db.execute(query, (job_id,))

        self.db.commit()
        return
    

    def finish_job(self, job_id: int):
        query = """
            UPDATE jobs
            SET status='finished', finished_at=NOW()
            WHERE train_id = %s;
        """

        self.db.execute(query, (job_id,))

        self.db.commit()
        return


    def get_dataset_dir(self, train_id: int) -> str:
        query = 'SELECT file_path FROM files WHERE file_type = \'dataset_dir\' AND id = %s'
        self.db.execute(query, (train_id,))
        dataset_dir = self.db.fetch_one()
        dataset_dir = dataset_dir.get('file_path')

        return dataset_dir

