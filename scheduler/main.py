from time import *
from datetime import datetime
from database.pool import x

class Scheduler:
    def __init__(self):
        self.running = False
        pass

    
    def run(self):
        self.running = True

        while self.running:
            log_message('Retrieving active jobs...')
            jobs = self.retrieve_active_jobs()
            log_message(f'{len(jobs)} found.')

            for job in jobs:
                job_id = job['id']
                log_message(f'Executing job: {job_id}')
                self.execute_job(job)
                sleep(1)
            log_message('All jobs finished!')

        return

    def retrieve_active_jobs(self):
        sleep(1)
        jobs = [
            {'id': '1', 'name': 'job_a'},
            {'id': '2', 'name': 'job_b'},
            {'id': '3', 'name': 'job_c'},
        ]
        return jobs
    

    def execute_job(self, job):
        return


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