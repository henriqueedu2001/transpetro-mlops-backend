from pathlib import Path
from datetime import datetime
from jobs.job_status import *

class Job:
    def __init__(
        self,
        job_id: int,
        train_id: int,
        status: Status = Status.CREATED,
        created_at: datetime = None,
        scheduled_at: datetime = None,
        finished_at: datetime = None,
        epochs: int = None,
        batch: int = None,
        workers: int = None,
        dataset_dir: Path = None
    ):
        self.job_id = job_id
        self.train_id = train_id
        self.status = status
        self.created_at = created_at
        self.scheduled_at = scheduled_at
        self.finished_at = finished_at
        self.epochs = epochs
        self.batch = batch   
        self.workers = workers 
        self.dataset_dir = dataset_dir
        pass


    def __str__(self):
        job_str = ''
        job_str += f'\tjob_id: {self.job_id}\n'
        job_str += f'\ttrain_id: {self.train_id}\n'
        job_str += f'\tstatus: {self.status}\n'
        job_str += f'\tcreated_at: {self.created_at}\n'
        job_str += f'\tscheduled_at: {self.scheduled_at}\n'
        job_str += f'\tfinished_at: {self.finished_at}\n'
        job_str += f'\tepochs: {self.epochs}\n'
        job_str += f'\tbatch: {self.batch}\n'
        job_str += f'\tworkers: {self.workers}\n'
        job_str += f'\tdataset_dir: {self.dataset_dir}'
        return job_str