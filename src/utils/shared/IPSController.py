import os
import requests

from env_reader import EnvReader
from qoops_logger import Logger

logger = Logger().instance(f"(ITI) IPS Controller")
env_instance = EnvReader.get_instance().get_ips_envs()


class IPSController:

    def get_platform_data(self, community_id:str, customer_id:str, purpose:str):
        try:
            ips_host = os.environ['ACL_HOST']
            url = f'{ips_host}/api/read-configuration/{customer_id}/{community_id}/{purpose}'
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers)
            return 200, response
        except Exception as e:
            print(f"Error IPS endpoint: {e}")
            return 500, f"Error from IPS: {e}"
    
    def get_list_partners(self, community_id):
        try:
            ips_host = os.environ['ACL_HOST']
            url = f'{ips_host}/api/community/{community_id}/partners'
            payload = {}
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            return 200, response
        except Exception as e:
            print(f"Error IPS endpoint: {e}")
            return 500, f"Error from IPS: {e}"


class IpsV2Controller:

    """
    Ips Controller class for interacting with the IPS API.
    """

    def __init__(self):
        """
        Constructor for initializing the IpsV2Controller.

        The constructor reads the ACL_HOST from the environment variables and sets it as an instance variable.
        """
        self.ips_host = env_instance['ips_host']
        self.api_key = env_instance['api_key']
        self.consumer_id = env_instance['consumer_id']

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
                'Content-Type': 'application/json',
                'apikey': self.api_key,
                'x-ips-consumer-id': self.consumer_id
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
            url = f'{self.ips_host}/api/v2/community/getPartnerByCommunity/{community_id}'
            payload = {}
            headers = {
                'Content-Type': 'application/json',
                'apikey': self.api_key,
                'x-ips-consumer-id': self.consumer_id
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            return 200, response
        except Exception as e:
            logger.error(f"Error IPS endpoint: {e}")
            return 500, f"Error from IPS: {e}"


