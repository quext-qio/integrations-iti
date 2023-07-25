from cerberus import Validator
from Utils.Abstract.IValidator import IValidator
from Utils.CustomErrorHandler import CustomErrorHandler

class ValidationConstants:
    UUID_REGEX = "[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"

class SchemaRequestGet(IValidator):
    def __init__(self, _data):
        print(_data)
        self.schema_request_get = {
            "customerUUID": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.UUID_REGEX,
                'meta': {'regex': "Incorrect format of Customer UUID"}
            },
            "communityUUID": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.UUID_REGEX,
                'meta': {'regex': "Incorrect format of Community UUID"}
            },
        }
        self.data = _data

    def is_valid(self):
        validator = Validator(self.schema_request_get, error_handler=CustomErrorHandler(self.schema_request_get))
        if validator.validate(self.data):
            return True, {}
        else:
            return False, validator.errors