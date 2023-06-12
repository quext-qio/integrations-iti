import json

class Response:
    def __init__(self, statusCode: str, data: list, errors: list) -> None:
        """
        Initializes a new Response object.

        Args:
            statusCode (str): The status code of the response.
            data (list): The data to be included in the response.
            errors (list): Any errors or error messages associated with the response.
        """
        self.statusCode = statusCode
        self.data = data
        self.errors = errors

    def toDict(self) -> str:
        """
        Converts the Response object to a dictionary format.

        Returns:
            dict: The Response object represented as a dictionary.
        """
        return json.dumps({
            'statusCode': self.statusCode,
            'body': {
                'data': self.data,
                'errors': self.errors
            },
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'isBase64Encoded': False  
        })
