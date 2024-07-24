from enum import Enum

class RoleChoice(Enum):
    MANAGER = 'manager'
    QA = 'qa'
    DEVELOPER = 'developer'
    

class StatusChoice(Enum):
    OPEN = 'open'
    REVIEW = 'review'
    WORKING = 'working'
    AWAITINGREL = 'waiting release'
    WAITINGQA = 'waiting qa'
    