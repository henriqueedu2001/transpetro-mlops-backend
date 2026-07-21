import requests

class REST_API:
    def start_job(job_id):
        params = {'job_id': job_id}
        requests.post('http://localhost:8000/jobs/start', params=params)


    def finish_job(job_id):
        params = {'job_id': job_id}
        requests.post('http://localhost:8000/jobs/finish', params=params)