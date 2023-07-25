from cerberus import Validator


class SchemaRequestPost:
    def __init__(self, _data):
        print(_data)

        self.schema_request_post = {
            "application": {
                'required': True,
                'type': 'dict',
                'schema': {
                    "rentAmount": {
                        'required': True,
                        'type': 'integer'
                    },
                    "depositAmount": {
                        'required': True,
                        'type': 'integer',
                        'default': 1
                    },
                    "leaseTerm": {
                        'required': True,
                        'type': 'integer',
                        'default': 12
                    },
                    "photoIdVerified": {
                        'required': True,
                        'type': 'integer',
                        'default': 1
                    },
                    "applicants": {
                        'required': True,
                        'type': 'dict',
                        'schema': {
                            "applicant": {
                                'required': True,
                                'type': 'list',
                                'schema': {
                                    'type': 'dict',
                                    'schema': {
                                        'applicantType': {
                                            'required': True,
                                            'type': 'integer'
                                        },
                                        'firstName': {
                                            'required': True,
                                            'type': 'string'
                                        },
                                        'lastName': {
                                            'required': True,
                                            'type': 'string'
                                        },
                                        'dateOfBirth': {
                                            'required': True,
                                            'type': 'string'
                                        },
                                        'streetAddress': {
                                            'required': True,
                                            'type': 'string'
                                        },
                                        'city': {
                                            'required': True,
                                            'type': 'string'
                                        },
                                        'state': {
                                            'required': True,
                                            'type': 'string'
                                        },
                                        'postalCode': {
                                            'required': True,
                                            'type': 'integer'
                                        },
                                        'employmentStatus': {
                                            'required': True,
                                            'type': 'integer'
                                        },
                                        'employmentIncome': {
                                            'required': True,
                                            'min': 1,
                                            'type': 'integer'
                                        },
                                        'employmentIncomePeriod': {
                                            'required': True,
                                            'type': 'integer'
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        self.data = _data

    def isValid(self):
        validator = Validator(self.schema_request_post)
        if validator.validate(self.data):
            return True, {}
        else:
            return False, validator.errors