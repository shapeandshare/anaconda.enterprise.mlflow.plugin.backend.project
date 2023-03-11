""" Anaconda Enterprise Project Job Run State Type Definition """

from enum import Enum


class AEProjectJobRunStateType(str, Enum):
    """Anaconda Enterprise Project Job Run State Type Enumeration"""

    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"
    RUNNING = "running"
