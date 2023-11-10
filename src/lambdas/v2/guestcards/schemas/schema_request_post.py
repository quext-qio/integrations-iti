from cerberus import Validator
from utils.custom_error_handler import CustomErrorHandler
from utils.abstract.i_validator import IValidator

class ValidationConstants:
    EMAIL = '(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
    UUID = '[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}' 

class SchemaRequestPost(IValidator):
    def __init__(self, _data):
        self.schema = {
            "platformData": {
                "type": "dict",
                "required": True,
                "schema": {
                    "customerUUID": {
                        'required': True,
                        'type': 'string',
                        'empty': False,
                        'regex': ValidationConstants.UUID,
                        'meta': {'regex': "The UUID is not valid"}
                    },
                    "communityUUID": {
                        'required': True,
                        'type': 'string',
                        'empty': False,
                        'regex': ValidationConstants.UUID,
                        'meta': {'regex': "The UUID is not valid"}
                    }
                }
            },
            "guest": {
                "type": "dict",
                "required": True,
                "schema": {
                    "first_name": {
                        'required': True,
                        'type': 'string',
                        'empty': False
                    },
                    "last_name": {
                        'required': True,
                        'type': 'string',
                        'empty': False
                    },
                    "phone": {
                        'required': False,
                        'type': 'string',
                        'empty': False
                    },
                    "email": {
                        'required': True,
                        'type': 'string',
                        'empty': False,
                        'regex': ValidationConstants.EMAIL,
                        'meta': {'regex': "The email is not valid"}
                    }
                }
            },
            "guestComment": {
                'required': False,
                'type': 'string',
                'empty': False
            },
            "guestPreference": {
                "type": "dict",
                "required": True
            },
            "qContactID": {
                'required': False,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.UUID,
                'meta': {'regex': "The UUID is not valid"}
            },
            "source": {
                'required': False,
                'type': 'string',
                'empty': False
            },
            "tourScheduleData": {
                "type": "dict",
                "required": False,
                "empty": False,
            }
        }
        self.data = _data

    def is_valid(self):
        validator = Validator(self.schema, error_handler=CustomErrorHandler(self.schema))
        if validator.validate(self.data):
            return True, {}
        else:
            return False, validator.errors
