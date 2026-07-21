from time import *
from datetime import datetime
from jobs.job import Job
from jobs.job_status import Status
from database.database_manager import *
from database.repositories import *

class Scheduler:
    def __init__(self):
        self.running = False
        self.db = Database()
        self.repository = Repository(self.db)
        pass

    
    def run(self):
        self.running = True

        while self.running:
            log_message('Retrieving active jobs...')
            jobs = self.retrieve_active_jobs()
            log_message(f'{len(jobs)} jobs found.')

            for job in jobs:
                log_message(f'Executing the job:\n{job}')
                self.execute_job(job)
                sleep(1)
            log_message('All jobs finished!')

        return

    def retrieve_active_jobs(self):
        sleep(1)
        jobs = self.repository.get_active_jobs()
        jobs = [self._cast_job(job) for job in jobs] 
        
        return jobs
    

    def execute_job(self, job: Job):
        return
    

    def _cast_job(self, job: Dict) -> Job:
        return Job(
            job_id=job.get('id'),
            train_id=job.get('train_id'),
            status=job.get('status'),
            created_at=job.get('created_at'),
            scheduled_at=job.get('scheduled_at'),
            finished_at=job.get('finished_at'),
            dataset_dir=job.get('file_path'),
            epochs=job.get('epochs'),
            batch=job.get('batch'),
            workers=job.get('workers')
        )


def log_message(message: str):
    """Logs the message, by printing it with the current timestamp.

    Args:
        message (str): the log message
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")


def main():
    scheduler = Scheduler()
    scheduler.run()
    return

if __name__ == '__main__':
    main()