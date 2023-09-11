from cerberus import Validator
from utils.abstract.i_validator import IValidator
from utils.custom_error_handler import CustomErrorHandler

class ValidationConstants:
    UUID = '[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}'
    DATE_YYYY_MM_DD = r'\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[01])'

class SchemaRequestPost(IValidator):
    def __init__(self, _data):
        self.schema_request_post = {
            # Path Parameters
            "customerUUID": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.UUID,
                'meta': {'regex': "The customerUUID is not valid"}
            },
            "action": {
                'required': True,
                'type': 'string',
                'empty': False,
                'allowed': ['unitsAndFloorPlans', 'residents', 'prospects', 'chargeCodes', 'properties', 'transactions', 'customerEvents']
            },
            "communityUUID": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.UUID,
                'meta': {'regex': "The communityUUID is not valid"}
            },
            # Body
            "move_in_date": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.DATE_YYYY_MM_DD,
                'meta': {'regex': "The move_in_date is not valid"}
            },
            "move_out_date": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.DATE_YYYY_MM_DD,
                'meta': {'regex': "The move_out_date is not valid"}
            },
        }
        self.data = _data

    def is_valid(self):
        validator = Validator(self.schema_request_post, error_handler=CustomErrorHandler(self.schema_request_post))
        if validator.validate(self.data):
            return True, {}
        else:
            return False, validator.errors