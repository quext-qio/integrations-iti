from cerberus import Validator
from utils.abstract.i_validator import IValidator
from utils.custom_error_handler import CustomErrorHandler

class ValidationConstants:
    EMAIL = '(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'

class SchemaRequestPost(IValidator):
    def __init__(self, _data):
        self.schema_request_post = {
            "email": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.EMAIL,
                'meta': {'regex': "The email is not valid"}
            },
            "fullName": {
                'required': True,
                'type': 'string',
                'empty': False
            },
            "userType": {
                'required': True,
                'type': 'string',
                'empty': False,
                'allowed': ['payer']
            },
        }
        self.data = _data

    def is_valid(self):
        validator = Validator(self.schema_request_post, error_handler=CustomErrorHandler(self.schema_request_post))
        if validator.validate(self.data):
            return True, {}
        else:
            return False, validator.errors