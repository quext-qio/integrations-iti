import json
import requests
import os
from datetime import datetime
from abstract.service_interface import ServiceInterface
from utils.mapper.bedroom_mapping import bedroom_mapping
from utils.service_response import ServiceResponse
from constants.mri_constants import *

class MRIService(ServiceInterface):

    def get_data(self, body, ips, logger):
        logger.info(f"Getting data from MRI")
        pass