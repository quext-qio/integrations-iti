import os
import requests

from qoops_logger import Logger

logger = Logger().instance(f"(ITI) IPS Controller")


class IPSController:

    """
    Ips Controller class for interacting with the IPS API.
    """

    def __init__(self):
        """
        Constructor for initializing the IpsV2Controller.

        The constructor reads the ACL_HOST from the environment variables and sets it as an instance variable.
        """
        self.ips_host = os.environ.get('ACL_HOST')

    def get_platform_data(self, community_id: str, purpose: str):
        """
        Get platform data from the IPS API.

        Args:
            community_id (str): The ID of the community.
            purpose (str): The purpose for retrieving configuration data.

        Returns:
            tuple: A tuple containing the HTTP status code and the API response.
        """
        try:
            url = f'{self.ips_host}/api/v2/parameters/read-configuration/{community_id}/{purpose}'
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers)
            return 200, response
        except Exception as e:
            logger.error(f"Error IPS endpoint: {e}")
            return 500, f"Error from IPS: {e}"

    def get_list_partners(self, community_id):
        """
        Get a list of partners for a given community from the IPS API.

        Args:
            community_id (str): The ID of the community.

        Returns:
            tuple: A tuple containing the HTTP status code and the API response.
        """
        try:
            url = f'{self.ips_host}/api/community/{community_id}/partners'
            payload = {}
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            return 200, response
        except Exception as e:
            logger.error(f"Error IPS endpoint: {e}")
            return 500, f"Error from IPS: {e}"


