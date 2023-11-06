from dataclasses import dataclass

@dataclass
class Employee:
    id: int
    employee_id: str
    username: str
    first_name: str
    last_name: str
    status: str
    dates: dict