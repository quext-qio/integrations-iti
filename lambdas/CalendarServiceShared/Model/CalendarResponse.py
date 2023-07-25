from pydantic import BaseModel
from typing import Optional


class Availability(BaseModel):
    timeSlot: Optional[str]
    lengthInMins: Optional[int] = 15
    slot: Optional[str] = 'Available'