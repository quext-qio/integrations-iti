import re
from typing import Optional, List
from pydantic import BaseModel, field_validator
from src.lambdas.v3.constants.v3_constants import V3Constants


class CustomerPreference(BaseModel):
    """
    Model representing customer preferences.
    """
    date_needed: str
    no_of_occupants: int
    desired_rent_min: int
    desired_rent_max: int
    move_in_reason: str
    desired_num_of_beds: List[str]
    desired_num_of_baths: List[int]
    lease_term_months: int
    desired_square_feet: str
    comment: str = ""
    target_move_in_date: str
    transportation: str
    special_requests: str = ""
    preferred_communication: List[str]


class TourScheduleData(BaseModel):
    """
    Model representing tour schedule data.
    """
    appointment_date: str
    task_notes: str
    duration: str
    agent_name: str


class InteractionActivity(BaseModel):
    """
    Model representing interaction activity.
    """
    interactionType: Optional[str]
    interactionDate: Optional[str]
    interactionResult: Optional[str]
    interactionNotes: Optional[str]
    data: Optional[dict]


class Interactions(BaseModel):
    """
    Model representing interactions.
    """
    interactions_activity: List[InteractionActivity]


class GuestCardSchema(BaseModel):
    """
    Model representing a guest card.
    """
    community_id: str
    customer_id: str
    purpose_name: str = "guestCards"
    category_name: str = "ITI"
    first_name: str
    middle_name: str
    last_name: str
    email: str = ""
    address_type: str
    address_line_1: str
    address_line_2: Optional[str]
    city: str
    state: str
    zip_code: str
    date_of_birth: str
    cell_phone: str
    home_phone: str = ""
    office_phone: str = ""
    comments: str
    customer_preference: CustomerPreference
    initial_visit: str
    tour_schedule_data: TourScheduleData
    interactions: Interactions
    source: str

    @field_validator('community_id')
    @classmethod
    def validate_community_id(cls, value):
        """
        Validates the community ID format.

        Args:
            value (str): The community ID to validate.

        Returns:
            str: The validated community ID.

        Raises:
            ValueError: If the community ID format is invalid.
        """
        if not re.match(V3Constants.UUID, value):
            raise ValueError("Invalid community id")
        return value

    @field_validator('customer_id')
    @classmethod
    def validate_customer_id(cls, value):
        """
        Validates the customer ID format.

        Args:
            value (str): The customer ID to validate.

        Returns:
            str: The validated customer ID.

        Raises:
            ValueError: If the customer ID format is invalid.
        """
        if not re.match(V3Constants.UUID, value):
            raise ValueError("Invalid customer id")
        return value

    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        """
        Validates the email format.

        Args:
            value (str): The email to validate.

        Returns:
            str: The validated email.

        Raises:
            ValueError: If the email format is invalid.
        """
        if not re.match(V3Constants.EMAIL, value):
            raise ValueError("Invalid email format")
        return value

    class Config:
        extra = 'allow'
        allow_mutation = True
