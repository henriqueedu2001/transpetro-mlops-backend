from datetime import datetime
from typing import *
from app.database.database_manager import Database


class Repository:
    def __init__(self, db: Database):
        self.db = db 