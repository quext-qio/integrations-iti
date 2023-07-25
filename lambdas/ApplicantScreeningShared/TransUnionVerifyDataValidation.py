from cerberus import Validator


class ValidationConstants:
    PHONE = '^(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$'
    EMAIL = '(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'


class SchemaRequestPost:
    def __init__(self, _data):
        print(_data)
        self.schema_request_post_verify = {
            "CustomParameters": {
                'required': False,
                'empty': True,
                'nullable': True,
                'type': 'list'
            },
            "DeviceSessionId": {
                'required': False,
                'nullable': True,
                'type': 'string'
            },
            "Applicant": {
                'required': True,
                'type': 'dict',
                'schema': {
                    "FirstName": {
                        'required': True,
                        'type': 'string'
                    },
                    "LastName": {
                        'required': True,
                        'type': 'string'
                    },
                    "MiddleName": {
                        'empty': True,
                        'type': 'string'
                    },
                    "Suffix": {
                        'empty': True,
                        'type': 'string'
                    },
                    "BirthDate": {
                        'required': True,
                        'type': 'string'
                    },
                    "Ssn": {
                        'required': True,
                        'type': 'string'
                    },
                    "Phone": {
                        'required': True,
                        'type': 'string',
                        'regex': ValidationConstants.PHONE
                    },
                    "EmailAddress": {
                        'required': True,
                        'regex': ValidationConstants.EMAIL
                    },
                    "IdentificationNumber": {
                        'required': True,
                        'type': 'string'
                    },
                    "IdentificationType": {
                        'type': 'string',
                        'empty': True,
                    },
                    "IdentificationState": {
                        'required': True,
                        'type': 'string'
                    },
                    "CustomParameters": {
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
                                    'type': 'string'
                                },
                                "City": {
                                    'required': True,
                                    'type': 'string'
                                },
                                "State": {
                                    'required': True,
                                    'type': 'string'
                                },
                                "PostalCode": {
                                    'required': True,
                                    'type': 'string'
                                },
                                "Country": {
                                    'required': True,
                                    'type': 'string'
                                },
                                "AddressType": {
                                    'required': True,
                                    'type': 'string'
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
                'type': 'string'
            },
            "CustomParameters": {
                'required': False,
                'type': 'list',
                'empty': True,
                'nullable': True
            },
            "DeviceSessionId": {
                'required': False,
                'nullable': True,
                'type': 'string'
            }
        }
        self.data = _data

    def isValidVerify(self):
        validator = Validator(self.schema_request_post_verify)
        if validator.validate(self.data):
            return True, {}
        else:
            return False, validator.errors

    def isValidEvaluate(self):
        validator = Validator(self.schema_request_post_evaluate)
        if validator.validate(self.data):
            return True, {}
        else:
            return False, validator.errors