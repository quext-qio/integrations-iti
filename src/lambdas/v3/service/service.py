import json
import uuid

from qoops_logger import Logger
from src.lambdas.v3.handler.end_point_handler import EndpointHandler
from src.lambdas.v3.handler.error_response_handler import ErrorResponse
from src.lambdas.v3.handler.protocol_handler import ProtocolHandler
from src.lambdas.v3.handler.response_handler import ResponseHandler
from src.lambdas.v3.mapper.mapper import FunctionalityMapper
from src.lambdas.v3.mapper.template_mapper import TemplateMapper


logger = Logger().instance('Partner generic service')


class PartnerGenericService:
    """
    Service class for handling external API calls.
    """

    @staticmethod
    def make_api_request(request_data):
        """
        Static method to make an external API call.

        Args:
            request_data (dict): Data for making the API call.

        Returns:
            dict: Constructed response for the respective request.
        """
        # Get API info for the specified purpose
        try:
            purpose_endpoints = EndpointHandler.get_api_info(request_data)
            end_point_data = request_data

            # Iterate over each endpoint for the purpose
            for end_point in purpose_endpoints:
                # Identify the protocol
                protocol = ProtocolHandler.get_protocol(end_point.protocol.lower())
                end_point_data.partner_endpoint_name = end_point.endpoint_name
                # Pre-process the request data if necessary
                end_point_data = FunctionalityMapper.pre_process_request_data(end_point_data)

                # Check if request processing is needed
                if end_point_data.process_request and end_point_data.process_request == True:
                    # Populate Jinja values in the request body template
                    end_point_data.request_id = str(uuid.uuid1())
                    request_body = TemplateMapper.populate_jinja_values(template_values=end_point_data,
                                                                        template=end_point.template)

                    # end_point_data = partner.partner_object.get_params(end_point_data)
                    end_point_data = FunctionalityMapper.get_params(end_point_data)
                    headers = FunctionalityMapper.get_headers(end_point_data.partner_name, json.loads(end_point.headers))
                    # Make the external API call
                    end_point_response = protocol(method=end_point.request_method,
                                                  url=f"{end_point.host_name}{end_point.url_path}/{end_point.endpoint_name}",
                                                  headers=headers,
                                                  params=end_point_data.request_params,
                                                  body=json.dumps(request_body)).make_request()

                    # Validate and construct the response
                    end_point_data, response = ResponseHandler().handle_api_response(request_data=end_point_data,
                                                                                     response=end_point_response)
                    # Return response if not valid
                    if not end_point_data.valid_response:
                        return response

            # Construct and return the final response
            return ResponseHandler.construct_response(end_point_data)
        except ConnectionError as ce:
            logger.error(str(ce))
            return ErrorResponse(status_code=500, message=str(ce)).format_response()


