from cerberus import Validator
from utils.abstract.i_validator import IValidator
from utils.custom_error_handler import CustomErrorHandler

class ValidationConstants:
    UUID = '[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}'
    DATE_YYYY_MM_DD = r'\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[01])'

# Define schemas for different actions
parameter_schema = {
                'required': True,
                'type': 'string',
                'empty': False,
                'allowed': ['get-charge-codes', 'tenants', 'lease-charges', 'get-recurring-transactions', 'get-properties', 'add-charges']
            }
property_id_schema = {
                'required': True,
                'type': 'integer',
                'empty': False
            }

schemas = {
    'get-charge-codes': {
        "Parameter": parameter_schema,
        "property_id": property_id_schema
    },
    'tenants': {
        "Parameter": parameter_schema,
        "property_id": property_id_schema
    },
    'lease-charges': {
        "Parameter": parameter_schema,
        "property_id": property_id_schema,
        "start_date": {
                'required': False,
                'type': 'string',
                'empty': True,
                'regex': ValidationConstants.DATE_YYYY_MM_DD,
                'meta': {'regex': "The start_date is not valid"}
            },
        "end_date": {
                'required': False,
                'type': 'string',
                'empty': True,
                'regex': ValidationConstants.DATE_YYYY_MM_DD,
                'meta': {'regex': "The end_date is not valid"}
            }
    },
    'get-recurring-transactions': {
        "Parameter": parameter_schema,
        "property_id": property_id_schema
        
    },
    'get-properties': {
       "Parameter": parameter_schema,
    },
    'add-charges': {
        "Parameter": parameter_schema,
        "charges": {
            'required': True,
            'type': 'list'
        },
    }
}

class SchemaRequestPost(IValidator):
    def __init__(self, _data, action):
        self.action = action
        self.schema_request_post = schemas.get(action, {})  # Get the schema for the given action
        self.data = _data

    def is_valid(self):
        validator = Validator(self.schema_request_post, error_handler=CustomErrorHandler(self.schema_request_post))
        
        # Lowercase all string values
        for clave, valor in self.data.items():
            if isinstance(valor, str):  
                self.data[clave] = valor.lower()
            
        if validator.validate(self.data):
            return True, {}
        else:
            return False, validator.errors

