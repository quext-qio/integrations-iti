from enum import Enum
from dataclasses import dataclass

class Status(Enum):
    ACTIVE = "Active"
    DECEASED = "Deceased"
    TERMINATED = "Terminated"
    TEST_EMPLOYEE = "TEST Employee"

@dataclass
class Employee:
    id: int
    employee_id: str
    username: str
    first_name: str
    last_name: str
    status: Status
    dates: dict