from cerberus import Validator
from datetime import datetime

from Utils.IdentityErrorHandler import IdentityErrorHandler
from Utils.CustomErrorHandler import CustomErrorHandler


class ValidationConstants:
    ALPHA = "^[A-Za-z\'\- ]+$"
    ALPHANUMERIC = "^[A-Za-z0-9]+$"
    INTEGERS = "^[0-9]+$"
    LETTERS = "^[a-zA-Z]+$"
    DATE = "^(0[1-9]|1[0-2])(0[1-9]|1\d|2\d|3[01])(19|20)\d{2}$"
    PHONE = '^(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$'
    EMAIL = '(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
    ADDRESS = "^[A-Za-z0-9\s]+$"


class IdentitySchema:
    def __init__(self, _data):
        self.schema_request_post_verify = {
            "CustomParameters": {
                'required': False,
                'type': 'list',
                'nullable': True
            },
            "DeviceSessionId": {
                'required': False,
                'type': 'string',
                'empty': True
            },
            "Applicant": {
                'required': True,
                'type': 'dict',
                'schema': {
                    "FirstName": {
                        'required': True,
                        'type': 'string',
                        'regex': ValidationConstants.ALPHA,
                        'minlength': 1,
                        'maxlength': 15
                    },
                    "LastName": {
                        'required': True,
                        'type': 'string',
                        'regex': ValidationConstants.ALPHA,
                        'minlength': 1,
                        'maxlength': 25
                    },
                    "MiddleName": {
                        'required': False,
                        'type': 'string',
                        'empty': True,
                        'regex': ValidationConstants.ALPHA,
                        'maxlength': 15
                    },
                    "Suffix": {
                        'required': False,
                        'type': 'string',
                        'empty': True,
                        'regex': ValidationConstants.ALPHANUMERIC,
                        'maxlength': 3
                    },
                    "BirthDate": {
                        'required': True,
                        'type': 'string',
                        'regex': ValidationConstants.DATE,
                        'minlength': 8,
                        'maxlength': 8
                    },
                    "Ssn": {
                        'required': True,
                        'type': 'string',
                        'regex': ValidationConstants.INTEGERS,
                        'minlength': 9,
                        'maxlength': 9
                    },
                    "Phone": {
                        'required': True,
                        'type': 'string',
                        'regex': ValidationConstants.PHONE,
                        'minlength': 10,
                        'maxlength': 10
                    },
                    "EmailAddress": {
                        'required': True,
                        'regex': ValidationConstants.EMAIL,
                        'maxlength': 100
                    },
                    "IdentificationNumber": {
                        'required': False,
                        'type': 'string',
                        'empty': True,
                        'regex': ValidationConstants.ALPHANUMERIC,
                        'maxlength': 50
                    },
                    "IdentificationType": {
                        'required': False,
                        'type': 'string',
                        'empty': True,
                        'maxlength': 50,
                        'allowed': ['DriversLicense', 'GovernmentIssuedPicture', 'MilitaryId', 'Visa']
                    },
                    "IdentificationState": {
                        'required': False,
                        'type': 'string',
                        'empty': True,
                        'minlength': 2,
                        'maxlength': 2,
                        'regex': ValidationConstants.LETTERS
                    },
                    "CustomParameters": {
                        'required': False,
                        'type': 'list',
                        'nullable': True,
                    },
                    "Addresses": {
                        'required': True,
                        'type': 'list',
                        'schema': {
                            'type': 'dict',
                            'schema': {
                                "StreetAddress": {
                                    'required': True,
                                    'type': 'string',
                                    'regex': ValidationConstants.ADDRESS,
                                    'minlength': 1,
                                    'maxlength': 100
                                },
                                "City": {
                                    'required': True,
                                    'type': 'string',
                                    'regex': ValidationConstants.ALPHA,
                                    'minlength': 1,
                                    'maxlength': 27
                                },
                                "State": {
                                    'required': True,
                                    'type': 'string',
                                    'regex': ValidationConstants.LETTERS,
                                    'minlength': 2,
                                    'maxlength': 2
                                },
                                "PostalCode": {
                                    'required': True,
                                    'type': 'string',
                                    'regex': ValidationConstants.INTEGERS,
                                    'minlength': 5,
                                    'maxlength': 5
                                },
                                "Country": {
                                    'required': True,
                                    'type': 'string',
                                    'allowed': ['USA']
                                },
                                "AddressType": {
                                    'required': True,
                                    'type': 'string',
                                    'allowed': ['Current', 'Previous']
                                }
                            }
                        }
                    }
                }
            }
        }
        self.data = _data

        self.schema_request_post_evaluate = {
            "Answers": {
                'required': True,
                'type': 'list',
                'schema': {
                    'type': 'dict',
                    'schema': {
                        "QuestionKeyName": {
                            'required': True,
                            'type': 'string'
                        },
                        "SelectedChoiceKeyName": {
                            'required': True,
                            'type': 'string'
                        }
                    }
                }
            },
            "ReferenceNumber": {
                'required': True,
                'type': 'string',
                'regex': ValidationConstants.ALPHANUMERIC,
                'meta': {'regex': "ReferenceNumber can only contain letters and numbers."},
                'minlength': 8,
                'maxlength': 24
            },
            "CustomParameters": {
                'required': False,
                'type': 'list'
            },
            "DeviceSessionId": {
                'required': False,
                'type': 'string'
            }
        }
        self.data = _data

    def is_valid_verify(self):
        validator = Validator(self.schema_request_post_verify)

        if validator.validate(self.data):
            current_date_time = datetime.now()
            value_date_time = datetime.strptime(self.data['Applicant']['BirthDate'], "%m%d%Y") if "BirthDate" in self.data["Applicant"] else ""
            
            # extra validation to check the BirthDate since it should be less than the current date
            if value_date_time != "" and value_date_time > current_date_time:
                return False, {
                    "data": {},
                    "error": {
                        "Applicant": [
                            {
                                "BirthDate": [
                                    "BirthDate should be less than the current date."
                                ]
                            }
                        ]
                    }
                }

            return True, {}
        else:
            error_handler = IdentityErrorHandler(validator.errors)

            return False, error_handler.update_error_messages()

    def is_valid_evaluate(self):
        validator = Validator(self.schema_request_post_evaluate, error_handler=CustomErrorHandler(self.schema_request_post_evaluate))

        if validator.validate(self.data):
            return True, {}
        else:
            return False, validator.errors

