from IPSController import IpsV2Controller
from qoops_logger import Logger
from src.lambdas.v3.service.service import PartnerGenericService
from src.lambdas.v3.utils.utils import Utils

logger = Logger().instance('Guest card v3 service')


class GuestCardService:
    """
    Service class for handling business logic.
    """

    @staticmethod
    def create_guest_card(request_data):
        """
        Static method to create a guest card.

        Args:
            request_data (pydantic object): Data for creating the guest card.

        Returns:
            dict: Result of creating the guest card.
        """
        # Retrieve platform data from IPS controller
        code, ips_response = IpsV2Controller().get_platform_data(request_data.community_id, purpose='guestCards')

        # Convert JSON data to object using custom utility function
        ips_data = Utils.json_to_object(ips_response.json())

        # Merge request data with IPS data
        request_data = Utils.merge_object_to_pydantic_object(request_data, ips_data)

        # Check if IPS request was successful
        if code != 200:
            error_message = f'Ips failed with error code {code} with message {ips_response["message"]}'
            raise Exception(error_message)

        # Check if IPS response contains necessary data
        if (not hasattr(request_data, 'purpose') or not hasattr(request_data.purpose, 'guestCards') or
                not hasattr(request_data.purpose.guestCards, 'partner_name')):
            error_message = f"IPS response does not contain platform for community {request_data.community_id}"
            logger.error(error_message)
            raise Exception(error_message)
        request_data.partner_name = request_data.purpose.guestCards.partner_name.lower()
        # Make external API call using PartnerGenericService
        return PartnerGenericService.make_api_request(request_data)

