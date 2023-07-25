from cerberus import Validator
from Utils.Abstract.IValidator import IValidator
from Utils.CustomErrorHandler import CustomErrorHandler

class ValidationConstants:
    UUID ="[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"

class SchemaRequestGet(IValidator):
    def __init__(self, _data):
        self.schema_request_get = {
            "email": {
                'required': False,
                'type': 'string',
                'empty': False
            },
            "prospectID": {
                'required': False,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.UUID,
                'meta': {'regex': "The prospectID is not valid"}
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