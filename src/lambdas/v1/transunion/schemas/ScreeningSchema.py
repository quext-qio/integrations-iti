from cerberus import Validator


class ValidationConstants:
    ALPHA = "^[A-Za-z.'\- ]*$"
    STREET_ADDRESS = "^[A-Za-z0-9 .,'()\x2D]*$"
    CITY = "^[A-Za-z .,'()\s-]*$"
    ALLOWED_STATES = ["AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY", "AA", "AE", "AP"]


class ScreeningSchema:
    def __init__(self, _data):

        self.schema_request_post = {
            "application": {
                'required': True,
                'type': 'dict',
                'schema': {
                    "rentAmount": {
                        'required': True,
                        'type': 'integer',
                        'min': 0,
                        'max': 25000
                    },
                    "depositAmount": {
                        'required': True,
                        'type': 'integer',
                        'default': 1,
                        'min': 0,
                        'max': 50000
                    },
                    "leaseTerm": {
                        'required': True,
                        'type': 'integer',
                        'default': 12,
                        'min': 1,
                        'max': 999
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
                                            'type': 'integer',
                                            'allowed': [1, 2]
                                        },
                                        'firstName': {
                                            'required': True,
                                            'type': 'string',
                                            'minlength': 2,
                                            'regex': ValidationConstants.ALPHA
                                        },
                                        'lastName': {
                                            'required': True,
                                            'type': 'string',
                                            'minlength': 2,
                                            'regex': ValidationConstants.ALPHA
                                        },
                                        'dateOfBirth': {
                                            'required': True,
                                            'type': 'string'
                                        },
                                        'streetAddress': {
                                            'required': True,
                                            'type': 'string',
                                            'regex': ValidationConstants.STREET_ADDRESS
                                        },
                                        'city': {
                                            'required': True,
                                            'type': 'string',
                                            'minlength': 3,
                                            'regex': ValidationConstants.CITY
                                        },
                                        'state': {
                                            'required': True,
                                            'type': 'string',
                                            'allowed': ValidationConstants.ALLOWED_STATES
                                        },
                                        'postalCode': {
                                            'required': True,
                                            'type': 'integer',
                                            'check_with': self.check_postal_code_length
                                        },
                                        'employmentStatus': {
                                            'required': True,
                                            'type': 'integer',
                                            'allowed': [1, 2, 3, 4]
                                        },
                                        'employmentIncome': {
                                            'required': True,
                                            'type': 'integer',
                                            'default': 1
                                        },
                                        'employmentIncomePeriod': {
                                            'required': True,
                                            'type': 'integer',
                                            'default': 1,
                                            'allowed': [1, 2, 3]
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

    def check_postal_code_length(self, field, value, error):
        if len(str(value)) != 5 and len(str(value)) != 9:
            error(field, f"{field} length is limited to 5 or 9 characters.")

    def is_valid(self):
        validator = Validator(self.schema_request_post)
        if validator.validate(self.data):
            applicant_type = False
            applicant_errors = []

            # extra validations required
            for index, applicant in enumerate(self.data["application"]["applicants"]["applicant"]):
                # checks if theres at least one applicant with applicantType = 1.
                if applicant["applicantType"] == 1 and applicant_type == False:
                    applicant_type = True
                
                # employmentIncome validations
                if applicant["employmentStatus"] == 1 and applicant["employmentIncome"] <= 0:
                    applicant_errors.append({
                        str(index): [
                            {
                                "employmentIncome": [
                                    "Required to be > 0 when employmentStatus = 1."
                                ]
                            }
                        ]
                    })
                elif applicant["employmentStatus"] != 1 and applicant["employmentIncome"] < 0:
                    applicant_errors.append({
                        str(index): [
                            {
                                "employmentIncome": [
                                    "Required to be >= 0."
                                ]
                            }
                        ]
                    })

            # applicantType error handler
            if applicant_type == False:
                return False, {
                    "application": [
                        {
                            "applicants": [
                                {
                                    "applicant": [
                                        {
                                            "applicantType": [
                                                "A valid request must include at least one applicant with an applicantType = 1."
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            # employmentIncome error handler
            elif len(applicant_errors) > 0:
                return False, {
                    "application": [
                        {
                            "applicants": [
                                {
                                    "applicant": applicant_errors
                                }
                            ]
                        }
                    ]
                }

            return True, {}
        else:
            return False, validator.errors

