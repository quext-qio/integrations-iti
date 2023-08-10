from cerberus import Validator
from utils.abstract.i_validator import IValidator
from utils.custom_error_handler import CustomErrorHandler

class SchemaRequestPost(IValidator):
    def __init__(self, _data):
        self.schema_request_post = {
            "query": {
                'required': True,
                'type': 'string',
                'empty': False,
            },
        }
        self.data = _data

    def is_valid(self):
        validator = Validator(self.schema_request_post, error_handler=CustomErrorHandler(self.schema_request_post))
        if validator.validate(self.data):
            return True, {}
        else:
            return False, validator.errors