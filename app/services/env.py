import os
from dotenv import load_dotenv

load_dotenv()

class EnvironmentVariables:
    def __init__(self):
        self.MY_SECRET = os.getenv('MY_SECRET')
        pass


environment_variables = EnvironmentVariables()


def get_env_variables():
    return environment_variables