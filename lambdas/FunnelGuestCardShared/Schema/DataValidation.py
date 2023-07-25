from cerberus import Validator
from Utils.Abstract.IValidator import IValidator

class ValidationConstants:
    PHONE = '^(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$'
    EMAIL = '(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'


class SchemaRequestPost(IValidator):
    def __init__(self, _data):
        print(_data)
        self.schema_request_post = {
            "first_name": {
                'required': True,
                'type': 'string'
            },
            "last_name": {
                'required': True,
                'type': 'string'
            },
            "email": {
                'required': True,
                'type': 'string',
                'regex': ValidationConstants.EMAIL
            },
            "phone_1": {
                'type': 'string',
                'empty': True,
                'nullable': True,
                'regex': ValidationConstants.PHONE
            },
            "phone_2": {
                'type': 'string',
                'empty': True,
                'nullable': True,
                'regex': ValidationConstants.PHONE
            },
            "is_primary": {
                'nullable': True,
                'type': 'boolean'
            },
        }
        self.data = _data

    def is_valid(self):
        validator = Validator(self.schema_request_post)
        if validator.validate(self.data):
            return True, {}
        else:
            return False, validator.errors