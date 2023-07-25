from cerberus import Validator
from Utils.Abstract.IValidator import IValidator
from Utils.CustomErrorHandler import CustomErrorHandler

class ValidationConstants:
    UUID ="[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"

class SchemaRequestPost(IValidator):
    def __init__(self, _data):
        self.schema_request_post = {
            "xml": {
                'required': True,
                'type': 'dict',
                'empty': False
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
            "tourSchedule_data" : {
                'required': False,
                'type': 'dict'
            }

        }
        self.data = _data

    def is_valid(self):
        validator = Validator(self.schema_request_post, error_handler=CustomErrorHandler(self.schema_request_post))
        if validator.validate(self.data):
            return True, {}
        else:
            return False, validator.errors