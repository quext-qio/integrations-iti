import json

class Response:
    def __init__(self, status_code: str, data: list, errors: list) -> None:
        """
        Initializes a new Response object.

        Args:
            statusCode (str): The status code of the response.
            data (list): The data to be included in the response.
            errors (list): Any errors or error messages associated with the response.
        """
        self.status_code = status_code
        self.data = data
        self.errors = errors

    def toDict(self) -> dict:
        """
        Converts the Response object to a dictionary format.

        Returns:
            dict: The Response object represented as a dictionary.
        """
        return {
            'statusCode': self.status_code,
            'body': json.dumps({
                'data': self.data,
                'errors': self.errors,
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
