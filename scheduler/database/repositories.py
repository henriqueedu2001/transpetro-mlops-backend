from pathlib import Path
from datetime import datetime
from typing import *
from database.database_manager import Database

class Repository:
    def __init__(self, db: Database):
        self.db = db 
    

    def get_active_jobs(self) -> List[Dict]:
        query = """
            SELECT * FROM jobs
            INNER JOIN files 
                ON jobs.train_id  = files.train_id  
            WHERE file_type = 'dataset_dir' AND status = 'created'
            ORDER BY created_at
        """
        self.db.execute(query)
        jobs = self.db.fetch_all()
        return jobs
    

