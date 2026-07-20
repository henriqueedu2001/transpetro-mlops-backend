from enum import Enum

class Status(Enum):
    CREATED = 'created'
    PROCESSING = 'processing'
    FINISHED = 'finished'
    CANCELLED = 'cancelled'