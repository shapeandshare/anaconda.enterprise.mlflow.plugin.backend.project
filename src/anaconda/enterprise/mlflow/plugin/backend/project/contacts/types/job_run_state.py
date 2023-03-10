from enum import Enum


class AEProjectJobRunState(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"
    RUNNING = "running"
