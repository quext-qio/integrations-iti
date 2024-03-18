import json


class ErrorResponse:
    """
    Class to represent an error response.

    Attributes:
        status_code (int): The status code of the error response.
        message (str): The error message.
    """

    def __init__(self, status_code, message):
        """
        Initializes an error response object with the provided status code and message.

        Args:
            status_code (int): The status code of the error response.
            message (str): The error message.
        """
        self.status_code = status_code
        self.message = message

    def format_response(self):
        """
        Formats the error response.

        Returns:
            dict: The formatted error response.
        """
        return {
            'statusCode': self.status_code,
            'body': json.dumps({
                'data': {},
                'error': {"message": f"{self.message}"},
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'isBase64Encoded': False
        }
