from src.lambdas.v3.mapper.partners.entrata.entrata_fucntions import EntrataFunctions
from src.lambdas.v3.utils.utils import Utils

request_functionality_mapper = {
    "entrata": {
        "properties": EntrataFunctions().pre_process_entrata_request_data_for_time_availability,
        "leads": EntrataFunctions().pre_process_entrata_request_data_for_guest_card}
}

response_functionality_mapper = {
    "entrata": {
        "properties": EntrataFunctions().post_process_entrata_response_data_for_time_availability,
        "leads": EntrataFunctions().post_process_entrata_response_data_for_guest_card}
}

response_constructor_mapper = {
    "guestCards": Utils().construct_guest_card_response
}

response_validator_mapper = {

    "entrata": {
        "properties": EntrataFunctions().validate_time_availability,
        "leads": EntrataFunctions().validate_guest_card_response}
}

header_mapper = {
    "entrata": EntrataFunctions().get_headers
}

param_mapper = {
    "entrata": EntrataFunctions().get_params
}


class FunctionalityMapper:
    """
    Class containing static methods for mapping functionality based on partner and endpoint names.
    """

    @staticmethod
    def post_process_response_data(request_data, response):
        """
        Performs post-processing on the response data based on partner and endpoint names.

        Args:
            request_data: The request data containing partner name and endpoint name.
            response: The response data received from the API.

        Returns:
            The processed request data and response data tuple if a post-processing function is found,
            otherwise returns the original request data and response data.
        """
        post_process_function = response_functionality_mapper[request_data.partner_name][
            request_data.partner_endpoint_name] \
            if request_data.partner_name in response_functionality_mapper and \
               request_data.partner_endpoint_name in response_functionality_mapper[request_data.partner_name] \
            else None

        return post_process_function(request_data, response) if post_process_function else (request_data, response)

    @staticmethod
    def pre_process_request_data(request_data):
        """
        Performs pre-processing on the request data based on partner and endpoint names.

        Args:
            request_data: The request data containing partner name and endpoint name.

        Returns:
            The processed request data if a pre-processing function is found, otherwise returns the original request data.
        """
        pre_process_function = request_functionality_mapper[request_data.partner_name][
            request_data.partner_endpoint_name] \
            if request_data.partner_name in request_functionality_mapper and \
               request_data.partner_endpoint_name in request_functionality_mapper[request_data.partner_name] \
            else None

        return pre_process_function(request_data) if pre_process_function else request_data

    @staticmethod
    def construct_response(request_data):
        """
        Map and retrieve response construction functionality based on request data.

        Args:
            request_data: Data associated with the request.

        Returns:
            any: Response construction functionality if available, otherwise None.
        """
        return response_constructor_mapper[request_data.purpose_name](request_data) if (
                request_data.purpose_name in response_constructor_mapper) else None

    @staticmethod
    def response_validator(request_data):
        """
        Retrieves the response validator based on the partner name and endpoint name.

        Args:
            request_data: The request data containing partner name and endpoint name.

        Returns:
            The response validator function if found, otherwise None.
        """
        return response_validator_mapper[request_data.partner_name][request_data.partner_endpoint_name] \
            if request_data.partner_name in response_validator_mapper and \
               request_data.partner_endpoint_name in response_functionality_mapper[request_data.partner_name] \
            else None

    @staticmethod
    def get_params(request_data):
        """
        Retrieves parameters for the Entrata API request.

        Args:
            request_data: The request data containing partner name.

        Returns:
            Updated request data with parameters if found, otherwise the original request data.
        """
        return param_mapper[request_data.partner_name](request_data) if (
                request_data.partner_name in param_mapper) else request_data

    @staticmethod
    def get_headers(partner_name, headers):
        """
        Retrieves headers for the Entrata API request.

        Args:
            partner_name: The name of the partner.
            headers: The existing headers data.

        Returns:
            Updated headers data with partner-specific headers if found, otherwise the original headers data.
        """
        return header_mapper[partner_name](headers) if (partner_name in header_mapper) else headers
