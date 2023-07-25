from cerberus import Validator
from Utils.Abstract.IValidator import IValidator
from Utils.CustomErrorHandler import CustomErrorHandler

class ValidationConstants:
    UUID ="[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"
    DATE="^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$"
    EMAIL='(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
    PHONE = '^(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$'

class QuextSchemaRequestPost(IValidator):
    def __init__(self, _data):
        self.schema_request_post = {
            "firstName": {
                'required': True,
                'type': 'string',
                'empty': False,
            },
            "lastName": {
                'required': True,
                'type': 'string',
                'empty': False,
            },
            "email": {
                'required': True,
                'type': 'string',
                'empty': False,
                'regex': ValidationConstants.EMAIL,
                'meta': {'regex': "Invalid Email Format"}
            },
            "phone": {
                'required': False,
                'type': 'string',
                'empty': True,
                'regex': ValidationConstants.PHONE,
                'meta': {'regex': "Invalid Phone Format"}
            },
            "layout": {
                'required': False,
                'type': 'list',
            },
            "priceCeiling":{
                'required': False,
                'type': 'integer'
            },
            "moveInDate":{
                'required': True,
                'nullable': True,
                'type': 'string',
                'empty': True,
                'regex': ValidationConstants.DATE,
                'meta': {'regex': "Invalid Move_In_Date Format"}
            },
            "notes":{
                'required': True,
                'type': 'string',
                'empty': True,
            },
            "start":{
                'required': True,
                'type': 'string',
                'empty': False,
            },
            "source":{
                'required': True,
                'type': 'string',
                'empty': False,
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
        validator = Validator(self.schema_request_post, error_handler=CustomErrorHandler(self.schema_request_post))
        if validator.validate(self.data):
            return True, {}
        else:
            return False, validator.errors
            