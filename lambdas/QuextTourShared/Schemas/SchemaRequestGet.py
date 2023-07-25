from cerberus import Validator
from Utils.Abstract.IValidator import IValidator
from Utils.CustomErrorHandler import CustomErrorHandler

class ValidationConstants:
    UUID ="[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"
    DATE="^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$"

class SchemaRequestGet(IValidator):
    def __init__(self, _data):
        self.schema_request_get = {
            "fromDate": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.DATE,
                'meta': {'regex': "Invalid From_Date Format"}
            },
            "toDate": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.DATE,
                'meta': {'regex': "Invalid To_Date Format"}
            },
             "communityUUID": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.UUID,
                'meta': {'regex': "Invalid communityUUID Format"}
            },
            "customerUUID": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.UUID,
                'meta': {'regex': "Invalid customerUUID Format"}
            },
        }
        self.data = _data

    def is_valid(self):
        validator = Validator(self.schema_request_get, error_handler=CustomErrorHandler(self.schema_request_get))
        if validator.validate(self.data):
            return True, {}
        else:
            return False, validator.errors