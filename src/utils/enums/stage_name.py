from enum import Enum

class StageName(Enum):
    DEV = "dev"
    STAGE = "stage"
    PROD = "prod"
    RC = "rc"
    QA = "qa"