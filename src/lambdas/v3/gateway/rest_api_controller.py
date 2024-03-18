import json
import requests


class RestAPICaller:
    """
    Class to make REST API calls.

    This class allows making HTTP requests to a specified URL with customizable headers, parameters, and body.

    """

    def __init__(self, method="POST", url="", headers=None, params=None, body=None):
        """
        Initializes a RestAPICaller object.

        Args:
            method (str): HTTP method for the request (default is "POST").
            url (str): URL to which the request will be sent.
            headers (dict): Headers for the request (default is None).
            params (dict): Parameters for the request (default is None).
            body (str): Body of the request (default is None).
        """
        self.method = method
        self.url = url
        self.headers = headers
        self.params = params
        self.body = body

    def make_request(self):
        """
        Makes the REST API call.

        Returns:
            requests.Response: Response object containing the result of the API call.
        """
        return requests.request(
            self.method,
            url=self.url,
            headers=self.headers,
            params=self.params,
            data=json.loads(self.body)
        )
