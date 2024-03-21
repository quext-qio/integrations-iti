from cerberus import Validator
from utils.abstract.i_validator import IValidator
from utils.custom_error_handler import CustomErrorHandler

class ValidationConstants:
    UUID = '[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}'
    DATE_YYYY_MM_DD = r'\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[01])'

# Define schemas for different actions
customer_schema = {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.UUID,
                'meta': {'regex': "The customerUUID is not valid"}
            }
action_schema = {
                'required': True,
                'type': 'string',
                'empty': False,
                'allowed': ['unitsAndFloorPlans', 'unitsandfloorplans', 'residents', 'prospects', 'chargeCodes', 'chargecodes', 'properties', 'transactions', 'customerEvents', 'customerevents']
            }
community_schema ={
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.UUID,
                'meta': {'regex': "The communityUUID is not valid"}
            }

schemas = {
    'unitsandfloorplans': {
        "customerUUID": customer_schema,
        "action": action_schema,
        "communityUUID": community_schema
    },
    'properties': {
        "customerUUID": customer_schema,
        "action": action_schema,
        "communityUUID": community_schema
    },
    'residents': {
        "customerUUID": customer_schema,
        "action": action_schema,
        "communityUUID": community_schema,
        "move_in_date": {
                'required': False,
                'type': 'string',
                'empty': True,
                'regex': ValidationConstants.DATE_YYYY_MM_DD,
                'meta': {'regex': "The move_in_date is not valid"}
            },
        "move_out_date": {
                'required': False,
                'type': 'string',
                'empty': True,
                'regex': ValidationConstants.DATE_YYYY_MM_DD,
                'meta': {'regex': "The move_out_date is not valid"}
            }
    },
    'transactions': {
        "customerUUID": customer_schema,
        "action": action_schema,
        "communityUUID": community_schema,
        "start_date": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.DATE_YYYY_MM_DD,
                'meta': {'regex': "The move_in_date is not valid"}
            },
        "end_date": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.DATE_YYYY_MM_DD,
                'meta': {'regex': "The move_out_date is not valid"}
            },
        "resident_id": {
                'required': True,
                'type': 'string',
                'empty': False,
            },
    },
    'customerevents': {
        "customerUUID": customer_schema,
        "action": action_schema,
        "communityUUID": community_schema,
        "start_date": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.DATE_YYYY_MM_DD,
                'meta': {'regex': "The move_in_date is not valid"}
            },
        "end_date": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.DATE_YYYY_MM_DD,
                'meta': {'regex': "The move_out_date is not valid"}
            },
    },
    'chargecodes': {
        "customerUUID": customer_schema,
        "action": action_schema,
        "communityUUID": community_schema
    },
    'prospects': {
        "communityUUID": community_schema,
        "customerUUID": customer_schema,
        "action": action_schema,
        "create_date": {
                    'required': True,
                    'type': 'string',
                    'empty': False,
                    'regex': ValidationConstants.DATE_YYYY_MM_DD,
                    'meta': {'regex': "The create date is not valid"}
        }
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

