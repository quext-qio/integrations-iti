from cerberus import Validator
from utils.abstract.i_validator import IValidator
from utils.custom_error_handler import CustomErrorHandler

class RequestBodyPost(IValidator):
    def __init__(self, _data):
        self.schema_body_post = {
            "project_name": {
                'required': True,
                'type': 'string',
                'empty': False,
            },
            "ticket_summary": {
                'required': True,
                'type': 'string',
                'empty': False,
            },
            "ticket_description": {
                'required': True,
                'type': 'string',
                'empty': False,
            },
            "issue_type": {
                'required': True,
                'type': 'string',
                'empty': False,
                'allowed': ['Bug', 'Task']
            },
            "priority": {
                'required': True,
                'type': 'integer', 
                'min': 1, 
                'max': 5
            },
            'labels': {
                'type': 'list', 
                'schema': {
                    'type': 'string', 
                    #'regex': r'^\w+$'
                }, 
                'default': []
            },
            'list_issues': {
                'type': 'list', 
                'schema': {
                    'type': 'string'
                }, 
                'default': []
            },
            'testing': {
                # 'type': 'boolean', 
                # 'default': False
                'type': 'string', 
                'default': "false"
            },
            'remainder_after_repeats': {
                'type': 'integer',
                'default': 5,
            },
        }
        self.data = _data

    def is_valid(self):
        validator = Validator(self.schema_body_post, error_handler=CustomErrorHandler(self.schema_body_post))
        if validator.validate(self.data):
            return True, {}
        else:
            return False, validator.errors