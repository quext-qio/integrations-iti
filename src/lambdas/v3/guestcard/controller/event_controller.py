from src.lambdas.v3.guestcard.abstract.abstract import Controller
from src.lambdas.v3.guestcard.schema.guest_card_request_schema import GuestCardSchema
from src.lambdas.v3.guestcard.service.service import GuestCardService


class EventController(Controller):
    """
    Controller class for handling event-related operations.
    """

    def create_guest_card(self, request_data, context):
        """
        Creates a guest card based on the provided request data.

        Args:
            request_data (dict): The request data containing information for creating the guest card.
            context: The Lambda function execution context.

        Returns:
            dict: Response data from creating the guest card.
        """
        # Validate the incoming request data using the GuestCardSchema.
        validated_guest_card_data = GuestCardSchema(**request_data)

        # Delegate the creation of the guest card to the GuestCardService.
        return GuestCardService.create_guest_card(validated_guest_card_data)

