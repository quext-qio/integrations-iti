import json

from pydantic import ValidationError as PydanticValidationError

from acl import ACL
from qoops_logger import Logger
from src.lambdas.v3.guestcard.controller import api_controller, event_controller
from src.lambdas.v3.handler.error_response_handler import ErrorResponse

logger = Logger().instance('Guest card v3 lambda handler')


def lambda_handler(event, context):
    """
    Lambda handler function for processing incoming events.

    This function identifies the source of the request and routes it to the respective controller for further processing.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (LambdaContext): Lambda function execution context.

    Returns:
        dict: Response data to be returned by the Lambda function.
    """
    try:
        if "Records" in event:
            # If the event contains "Records", route the request to the ApiController for processing.
            return api_controller.ApiController().create_guest_card(json.loads(event['Records'][0].get('body')),
                                                                    context=context)
        elif 'httpMethod' in event and 'body' in event and event['body']:
            # If the event contains 'httpMethod' and 'body', route the request to the EventController for processing.
            input_data = json.loads(event['body'])
            is_acl_valid, response_acl = ACL.check_permitions(event)
            if not is_acl_valid:
                return response_acl
            return event_controller.EventController().create_guest_card(input_data, context)

    except PydanticValidationError as pye:
        # Handle Pydantic validation errors.
        logger.error(f'pydantic_validation_error: {pye}')
        return ErrorResponse(status_code=500, message=str(pye.json())).format_response()

    except Exception as e:
        # Handle other exceptions.
        logger.error(f'Exception occurred: {e}')
        return ErrorResponse(status_code=500, message=str(e)).format_response()

