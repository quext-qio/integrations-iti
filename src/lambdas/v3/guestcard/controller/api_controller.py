from src.lambdas.v3.guestcard.abstract.abstract import Controller
from src.lambdas.v3.guestcard.schema.guest_card_request_schema import GuestCardSchema
from src.lambdas.v3.guestcard.service.service import GuestCardService


class ApiController(Controller):
    """
    Controller class for handling API requests.
    """

    def create_guest_card(self, request_data, context):
        """
        Static method to create a guest card.

        Args:
            request_data (dict): Data for creating the guest card.
            context (dict): Context information related to the request.

        Returns:
            dict: Result of creating the guest card.
        """
        # Validate the guest card data
        validated_guest_card_data = GuestCardSchema(**request_data)

        # Create the guest card using the validated data
        return GuestCardService.create_guest_card(validated_guest_card_data)

