import json
import logging
import sys

from zato.server.service import Service

from DataPushPullShared.Utilities.DataController import QuextIntegrationConstants
from ExceptionHandling.Utilities.ErrorCode import StatusMapper, ErrorCode, ErrorConstants


class ErrorHandlingController:
    """
    Exception Handling Controller for handling all the exception and generate the error response
    based on the condition the exception were raised
    """

    @staticmethod
    def build_error_response(service: Service, exception: Exception):
        """
        Constructing Error Response for the given exception

        Parameters:
        -----------
        service: Service
            Service Class for which the response is built
        exception: Exception
            Exception occurred during the flow
        """
        logging.debug("Processing exception = {}".format(exception))

        if hasattr(exception, ErrorConstants.STATUS_CODE):
            service.response.status_code = exception.status_code
        if not hasattr(exception, ErrorConstants.ERROR_CODE):
            setattr(exception, ErrorConstants.ERROR_CODE, ErrorCode.ERROR_INTERNAL_ERROR)
        if not hasattr(exception, ErrorConstants.ERROR_MSG):
            setattr(exception, ErrorConstants.ERROR_MSG, exception)

        _error = {'ErrorCode': exception.error_code.name, ErrorConstants.MESSAGE: str(exception.error_msg)}
        errors = {QuextIntegrationConstants.DATA: {}, QuextIntegrationConstants.ERROR: _error}

        if not service.response.status_code:
            service.response.status_code = StatusMapper.get_status(exception.error_code)
        service.response.payload = json.dumps(errors)
