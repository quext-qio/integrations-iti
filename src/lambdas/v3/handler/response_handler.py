import json

from qoops_logger import Logger
from src.lambdas.v3.mapper.mapper import FunctionalityMapper

logger = Logger().instance('Response handler')


class ResponseHandler:
    """
    Class for handling API responses.
    """

    def handle_api_response(self, request_data, response):
        """
        Handles API responses by validating and post-processing them.

        Args:
            request_data: Data associated with the API request.
            response: API response received.

        Returns:
            Tuple: Contains updated request data and validated response.
        """
        request_data, validated_response = self.validate_response(request_data, response)

        if not request_data.valid_response:
            return request_data, validated_response

        return FunctionalityMapper.post_process_response_data(request_data, validated_response)

    @staticmethod
    def validate_response(request_data, response):
        """
        Validates the API response.

        Args:
            request_data: Data associated with the API request.
            response: API response received.

        Returns:
            Tuple: Contains updated request data and validated response.
        """
        response_validator_function = FunctionalityMapper.response_validator(request_data)

        return response_validator_function(request_data, response) if response_validator_function else (
            request_data, response)

    @staticmethod
    def construct_response(response):
        """
        Constructs the API response.

        Args:
            response: API response received.

        Returns:
            Constructed response.
        """
        return FunctionalityMapper.construct_response(response)

