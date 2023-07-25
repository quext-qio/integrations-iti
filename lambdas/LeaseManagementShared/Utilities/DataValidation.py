from enum import Enum

from LeaseManagementShared.Models.BlueMoonLeaseResponse import BaseResponse, BaseError
from LeaseManagementShared.Utilities.Convert import Convert
from LeaseManagementShared.Utilities.LeaseIntegrationConstants import LeaseIntegrationConstants
import collections

from cerberus import Validator
from multipledispatch import dispatch


class PlatformType(Enum):
    NONE = 0
    BLUEMOON = 1


class AuthorizationType(Enum):
    NONE = 0
    BlueMoonAuthorization = 1


class BasePlatformData:
    communityUUID: str
    customerUUID: str


class Schema(Enum):
    NONE = 0,
    CREATE_LEASE = 1,
    PLATFORM_DATA = 2,
    UPDATE_RESIDENTS = 3,
    GENERATE_PDF = 4,
    CREATE_ESIGNATURE = 5,
    DELETE_LEASE = 6


class ValidationConstants:
    UUID_REGEX = "[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"
    STREET_ADDRESS_REGEX = "^[0-9A-Za-z -]+$"
    DATE_REGEX = "^\d{4}(-|\/)((0[1-9])|(1[0-2]))(-|\/)((0[1-9])|([1-2][0-9])|(3[0-1]))$"
    UNIT_REGEX = "^[0-9A-Za-z\s_-]+$"
    NAME_REGEX = "^[A-Za-z '.-]+$"
    EMAIL_REGEX = "^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$"
    FAX_REGEX = "^\+[0-9]{1,3}-[0-9]{3}-[0-9]{7}$"
    AMOUNT_REGEX = "^[0-9]\d*(((,\d{3}){1})?(\.\d{0,2})?)$"
    CHARACTER_REGEX = "^[A-Za-z -]+$"
    NUMBER_REGEX = "^[0-9]+$"
    ZIP_CODE = "^[0-9]{5}(?:-[0-9]{4})?$"
    PET_DEPOSIT = ["securyes", 'securno']
    YEARLY_TERMINATE = ["termanyday", "termanymon"]
    YEARLY_TERMINATE_fact = ["termislimited", "not_termislimited"]
    YEAR_REGEX = "^\d{4}$"
    BOOLEAN_CHECK = ["false", "true"]
    REFUND_CHECK = ["depositcheckissuedjointly", "depositcheckoneresident"]
    OTHER_INSURANCE = ["insurancerequired", "insurancenotrequired"]
    PRORATED_RENT_DUE_MONTH = ["firstmo", "secondmo"]
    LEASE_TERMINATES = ["onexact", "onlast"]
    UNIT_COMES = ["unfurnsh", "furnsh"]
    ERROR_MESSAGES = 'errorMessages'
    ERROR_TYPE = 'errorType'
    URL_REGEX = "^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"
    PHONE_REGEX = "^(?:(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$"


class PlatformData:
    @staticmethod
    def getPlatformRequestData(_data: dict, purpose: str):
        error = {}
        param = {}
        _isValid, _error = Validate.schema(Schema.PLATFORM_DATA, _data)
        if _isValid:
            param = {
                LeaseIntegrationConstants.COMMUNITY_UUID: _data['communityUUID'],
                LeaseIntegrationConstants.CUSTOMER_UUID: _data['customerUUID'],
                LeaseIntegrationConstants.PURPOSE: purpose
            }
        else:
            error = _error
        return param, error

    @staticmethod
    def validatePlatformResponseData(_responseCode):
        _isValid = False
        _error = {}

        if _responseCode == 200:
            _isValid = True
        else:
            _error[LeaseIntegrationConstants.PLATFORM_DATA] = 'Invalid Platform Data'

        return _isValid, _error

    def getPlatformType(_type: str):
        """
            @desc: this method will check for the _type value and returns the platform type
            @param: _type string which contains platform name (eg: BLUEMOON)
            @return: platform type enum value
        """
        switcher = {
            'BLUEMOON': PlatformType.BLUEMOON
        }
        return switcher.get(_type, PlatformType.NONE)


class Validate:
    @staticmethod
    def schema(_schemaType, _data):
        """ Validate the _data schema with _schemaType and return appropriate validation status and validation errors"""
        _error = {}
        if isinstance(_schemaType, Schema):
            _schemaType = Validation_Schema[_schemaType]
        isValid, error = PYChecker().validate(_data, _schemaType)
        responseObj = BaseResponse()
        errorObj = BaseError()
        if not isValid:
            for k, v in error.items():
                _error[k] = ",".join(v)
            errorObj.errorMessages = _error
        responseObj.error = errorObj
        return isValid, Convert.toDict(responseObj)


class PYChecker(object):
    def __init__(self):
        self.validator = Validator()

    def _formatError(self, _input, key, output):
        if isinstance(_input, list):
            for item in _input:
                if isinstance(item, dict):
                    self._formatError(item, None, output)
                elif isinstance(item, str):
                    if 'regex' in item or 'missing' in item:
                        output[key].add("Invalid " + key)
                    else:
                        output[key].add(item)
        elif isinstance(_input, dict):
            for k, v in _input.items():
                self._formatError(v, k, output)

    @dispatch(dict, dict)
    def validate(self, field, schema):
        status = self.validator.validate(field, schema)
        output = collections.defaultdict(set)
        self._formatError(self.validator.errors, None, output)
        return status, output

    @dispatch(str, int, int)
    def validate(self, field: str, min_Length: int, max_Length: int):
        schema_value = {'fieldValue': field}
        schema = {
            'fieldValue': {
                'type': 'string',
                'minlength': min_Length,
                'maxlength': max_Length
            }
        }
        status = self.validator.validate(schema_value, schema)
        return status, self.validator.errors

    @dispatch(str, str)
    def validate(self, field, regex: str):
        schema_value = {'fieldValue': field}
        schema = {
            'fieldValue': {
                'type': 'string',
                'regex': regex
            }
        }
        status = self.validator.validate(schema_value, schema)
        return status, self.validator.errors

    @dispatch(int, int, int)
    def validate(self, field, minValue: int, maxValue):
        schema_value = {'fieldValue': field}
        schema = {
            'fieldValue': {
                'type': 'number',
                'min': minValue,
                'max': maxValue
            }
        }
        status = self.validator.validate(schema_value, schema)
        return status, self.validator.errors


Validation_Schema = {
    Schema.NONE: None,
    Schema.PLATFORM_DATA: {
        'communityUUID': {'required': True,
                          'type': 'string',
                          'regex': ValidationConstants.UUID_REGEX},
        'customerUUID': {'required': True,
                         'type': 'string',
                         'regex': ValidationConstants.UUID_REGEX},
        'leaseId': {
            'type': 'string',
            'regex': ValidationConstants.NUMBER_REGEX,
            'empty': True
        }
    },
    Schema.CREATE_LEASE: {
        'lease_data': {
            'required': True,
            'type': 'dict',
            'schema': {
                'address': {
                    'required': True,
                    'type': 'string',
                    'regex': ValidationConstants.STREET_ADDRESS_REGEX
                },
                'date_of_lease': {
                    'type': 'string',
                    'regex': ValidationConstants.DATE_REGEX,
                    'empty': True
                },
                'unit_number': {
                    'type': 'string',
                    'regex': ValidationConstants.UNIT_REGEX,
                    'required': True
                },
                'resident_information': {
                    'required': True,
                    'type': 'dict',
                    'schema': {
                        'resident': {
                            'type': 'list',
                            'required': True,
                            'schema': {
                                'type': 'string',
                                'regex': ValidationConstants.NAME_REGEX
                            }
                        },
                        'occupant': {
                            'type': 'list',
                            'empty': True,
                            'schema': {
                                'type': 'string',
                                'regex': ValidationConstants.NAME_REGEX
                            }
                        }
                    }
                },
                'maximum_guest_stay': {
                    'type': 'string',
                    'required': True,
                    'regex': ValidationConstants.NUMBER_REGEX
                },
                'lease_terms': {
                    'required': True,
                    'type': 'dict',
                    'schema': {
                        'lease_begin_date': {
                            'type': 'string',
                            'required': True,
                            'regex': ValidationConstants.DATE_REGEX,
                            'empty': True
                        },
                        'lease_end_date': {
                            'type': 'string',
                            'required': True,
                            'regex': ValidationConstants.DATE_REGEX,
                            'empty': True
                        },
                        'days_prorated': {
                            'type': 'string',
                            'empty': True,
                            'regex': ValidationConstants.NUMBER_REGEX
                        },
                        'prorated_rent': {
                            'type': 'string',
                            'empty': True,
                            'regex': ValidationConstants.AMOUNT_REGEX
                        },
                        'prorated_rent_per_day': {
                            'type': 'string',
                            'empty': True,
                            'regex': ValidationConstants.AMOUNT_REGEX
                        },
                        'prorated_rent_due_date': {
                            'type': 'string',
                            'regex': ValidationConstants.DATE_REGEX,
                            'empty': True
                        },
                        'prorated_rent_due_first_month': {
                            'type': 'string',
                            'regex': ValidationConstants.CHARACTER_REGEX,
                            'empty': True
                        },
                        'reletting_charge': {
                            'type': 'string',
                            'regex': ValidationConstants.AMOUNT_REGEX,
                            'empty': True
                        },
                        'reletting_charge_percent': {
                            'type': 'string',
                            'regex': ValidationConstants.NUMBER_REGEX,
                            'empty': True
                        },
                        'rent': {
                            'type': 'string',
                            'regex': ValidationConstants.AMOUNT_REGEX,
                            'empty': True
                        },
                        'security_deposit': {
                            'type': 'string',
                            'regex': ValidationConstants.AMOUNT_REGEX,
                            'empty': True
                        },
                        'security_deposit_includes_animal_deposit': {
                            'type': 'string',
                            'allowed': ValidationConstants.PET_DEPOSIT,
                            'empty': True
                        }
                    }
                },
                'security_deposit': {
                    'type': 'dict',
                    'schema': {
                        'security_deposit_refund_check_payable': {
                            'type': 'string',
                            'empty': True,
                            'allowed': ValidationConstants.REFUND_CHECK,
                            'excludes': 'security_deposit_refund_one_check_mailed_to'
                        },
                        'security_deposit_refund_one_check_mailed_to': {
                            'type': 'string',
                            'empty': True,
                            'regex': ValidationConstants.NAME_REGEX,
                            'excludes': 'security_deposit_refund_check_payable'
                        }
                    }
                }
            }
        },
        'student_lease': {
            'empty': True,
            'type': 'dict',
            'schema': {
                    'unit_number': {
                        'type': 'string',
                        'regex': ValidationConstants.UNIT_REGEX,
                        'required': True
                    },
                    'student_lease_bedroom_number': {
                        'type': 'string',
                        'empty': True,
                        'regex': ValidationConstants.NUMBER_REGEX
                    },
                    'student_lease_floor_plan': {
                        'type': 'boolean',
                        'empty': True,
                        'allowed': ValidationConstants.BOOLEAN_CHECK
                    },
                    'student_lease_total_lease_term_rent': {
                        'type': 'string',
                        'empty': True,
                        'regex': ValidationConstants.AMOUNT_REGEX
                    },
                    'student_lease_apartment': {
                        'type': 'string',
                        'empty': True,
                        'regex': ValidationConstants.CHARACTER_REGEX
                    },
                    'student_lease_monthly_installment': {
                        'type': 'string',
                        'empty': True,
                        'regex': ValidationConstants.AMOUNT_REGEX
                    },
                    'student_lease_bedroom_change_transfer_fee': {
                        'type': 'string',
                        'empty': True,
                        'regex': ValidationConstants.AMOUNT_REGEX
                    },
                    'student_lease_unit_transfer_fee': {
                        'type': 'string',
                        'empty': True,
                        'regex': ValidationConstants.AMOUNT_REGEX
                    },
                    'special_provision': {
                        'required': True,
                        'type': 'dict',
                        'schema': {
                            'student_housing_special_provisions': {
                                'type': 'string',
                                'empty': True,
                                'regex': ValidationConstants.CHARACTER_REGEX
                            }
                        }
                     }
            }
        },
        'other_charges': {
            'empty': True,
            'type': 'dict',
            'schema': {
                    'days_required_for_notice_of_lease_termination': {
                        'type': 'string',
                        'required': True,
                        'regex': ValidationConstants.NUMBER_REGEX
                    },
                    'additional_charges': {
                        'required': True,
                        'type': 'dict',
                        'schema': {
                            'rent_due_date': {
                                'type': 'string',
                                'required': True,
                                'regex': ValidationConstants.NUMBER_REGEX
                            },
                            'late_charge_initial_charge': {
                                'type': 'string',
                                'required': True,
                                'regex': ValidationConstants.AMOUNT_REGEX
                            },
                            'late_charge_percentage_of_rent': {
                                'type': 'string',
                                'required': True,
                                'regex': ValidationConstants.NUMBER_REGEX
                            },
                            'late_charge_daily_charge': {
                                'type': 'string',
                                'required': True,
                                'regex': ValidationConstants.AMOUNT_REGEX
                            },
                            'late_charge_daily_percent_of_rent': {
                                'type': 'string',
                                'required': True,
                                'regex': ValidationConstants.NUMBER_REGEX
                            },
                            'late_charge_daily_cannot_exceed_days': {
                                'type': 'string',
                                'required': True,
                                'regex': ValidationConstants.NUMBER_REGEX
                            },
                            'returned_check_charge': {
                                'type': 'string',
                                'required': True,
                                'regex': ValidationConstants.AMOUNT_REGEX
                            },
                            'pet_charge_initial_charge': {
                                'type': 'string',
                                'required': True,
                                'regex': ValidationConstants.AMOUNT_REGEX
                            },
                            'pet_charge_daily_charge': {
                                'type': 'string',
                                'required': True,
                                'regex': ValidationConstants.AMOUNT_REGEX
                            },
                            'monthly_pest_control_rent': {
                                'type': 'string',
                                'required': True,
                                'regex': ValidationConstants.AMOUNT_REGEX
                            },
                            'monthly_trash_rent': {
                                'type': 'string',
                                'required': True,
                                'regex': ValidationConstants.AMOUNT_REGEX
                            },
                            }
                    },
                    'keys': {
                        'required': True,
                        'type': 'dict',
                        'schema': {
                            'number_of_other_keys': {
                                'type': 'string',
                                'required': True,
                                'regex': ValidationConstants.NUMBER_REGEX
                            },
                            'number_of_mail_keys': {
                                'type': 'string',
                                'required': True,
                                'regex': ValidationConstants.NUMBER_REGEX
                            },
                            'other_key_type': {
                                'type': 'string',
                                'required': True,
                                'regex': ValidationConstants.CHARACTER_REGEX
                            },
                            'old_unit_number': {
                                'type': 'string',
                                'required': True,
                                'regex': ValidationConstants.NUMBER_REGEX
                            }

                        }

                    },
                    'insurance': {
                        'required': True,
                        'type': 'dict',
                        'schema': {
                            'renters_insurance_requirement': {
                                'type': 'string',
                                'required': True,
                                'allowed': ValidationConstants.OTHER_INSURANCE
                            }
                        }
                        }

            },

        },
        'special_provisions': {
                        'empty': True,
                        'type': 'dict',
                        'schema': {
                                'utility_services_paid_by_owner': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'utilities_gas': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'utilities_water': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'utilities_wastewater': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'utilities_electricity': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'utilities_trash': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'utilities_cable_tv': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'utilities_master_antenna': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'utilities_internet': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'utilities_stormwater_drainage': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'utilities_government_fees': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'utilities_other': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'electric_transfer_fee': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        }

                                    }
                                },
                                'special_provisions': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'special_provisions': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                        }
                                    }
                             },
                                'unit_comes': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'unit_furnished': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.UNIT_COMES
                                        }
                                    }
                                },
                                'pay_rent': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'pay_rent_on_site': {
                                            'type': 'string',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'pay_rent_at_online_site': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.UNIT_COMES
                                        },
                                        'pay_rent_address': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.URL_REGEX
                                        }
                                    }
                                },
                                'move_out_lease_will_terminate': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'lease_terminates_last_day_of_month': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.LEASE_TERMINATES
                                        }
                                    }
                                }

                        }

        },
        'attachments': {
                        'empty': True,
                        'type': 'dict',
                        'schema': {
                            'owner_representative': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'owners_representative_address': {
                                                'type': 'list',
                                                'empty': True,
                                                'schema': {
                                                    'type': 'string',
                                                    'regex': ValidationConstants.STREET_ADDRESS_REGEX
                                                 }
                                        },
                                        'owners_representative_telephone': {
                                                'type': 'string',
                                                'empty': True,
                                                'regex': ValidationConstants.PHONE_REGEX,
                                        },
                                        'owners_representative_fax': {
                                                'type': 'string',
                                                'empty': True,
                                                'regex': ValidationConstants.FAX_REGEX,
                                        },
                                        'owners_representative_after_hours_phone': {
                                                'type': 'string',
                                                'empty': True,
                                                'regex': ValidationConstants.PHONE_REGEX,
                                        }
                                    }
                            },
                            'locate_service': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'locator_address': {
                                                'type': 'string',
                                                'empty': True,
                                                'regex': ValidationConstants.STREET_ADDRESS_REGEX,
                                        },
                                        'locator_city_state_zip': {
                                                'type': 'string',
                                                'empty': True,
                                                'regex': ValidationConstants.ZIP_CODE,
                                        },
                                        'locator_name': {
                                                'type': 'string',
                                                'empty': True,
                                                'regex': ValidationConstants.NUMBER_REGEX,
                                        },
                                        'locator_phone': {
                                                'type': 'string',
                                                'empty': True,
                                                'regex': ValidationConstants.PHONE_REGEX,
                                        }
                                    }
                            },
                            'copies_and_attachments': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'addendum_access_gate': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_additional_special_provisions': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_utility_allocation': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'regex': ValidationConstants.BOOLEAN_CHECK,
                                                'schema': {
                                                    'addendum_utility_allocation_gas': {
                                                            'type': 'boolean',
                                                            'empty': True,
                                                            'allowed': ValidationConstants.BOOLEAN_CHECK,
                                                    },
                                                    'addendum_utility_allocation_electricity': {
                                                            'type': 'string',
                                                            'empty': True,
                                                            'allowed': ValidationConstants.BOOLEAN_CHECK,
                                                    },
                                                    'addendum_utility_allocation_cable_tv': {
                                                            'type': 'string',
                                                            'empty': True,
                                                            'allowed': ValidationConstants.BOOLEAN_CHECK,
                                                    },
                                                    'addendum_utility_allocation_trash': {
                                                            'type': 'string',
                                                            'empty': True,
                                                            'allowed': ValidationConstants.BOOLEAN_CHECK,
                                                    },
                                                    'addendum_utility_allocation_water': {
                                                            'type': 'string',
                                                            'empty': True,
                                                            'allowed': ValidationConstants.BOOLEAN_CHECK,
                                                    },
                                                    'addendum_utility_allocation_central_system_costs': {
                                                            'type': 'string',
                                                            'empty': True,
                                                            'allowed': ValidationConstants.BOOLEAN_CHECK,
                                                    },
                                                    'addendum_utility_allocation_stormwater_drainage': {
                                                            'type': 'string',
                                                            'empty': True,
                                                            'allowed': ValidationConstants.BOOLEAN_CHECK,
                                                    },
                                                    'addendum_utility_allocation_services_govt_fees': {
                                                            'type': 'string',
                                                            'empty': True,
                                                            'allowed': ValidationConstants.BOOLEAN_CHECK,
                                                    }
                                                }
                                        },
                                        'addendum_animal_addendum': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_apartment_rules': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_asbestos': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_bed_bug': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_early_termination': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_enclosed_garage': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_intrusion_alarm': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_inventory_and_condition': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_lead_hazard_disclosure': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_lease_contract_guaranty': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_affordable_housing': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_legal_description': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_military_scra': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_mold': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_move_out_cleaning_instructions': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_notice_of_intent_to_move_out': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_parking_permit_quantity': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.NUMBER_REGEX
                                        },
                                        'addendum_parking_permit': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_rent_concession': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_renters_insurance': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_repair_request_form': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_satellite_dish': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_security_guidelines': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_tceq_guide': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'addendum_utility_submetering': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'regex': ValidationConstants.BOOLEAN_CHECK,
                                                'schema': {
                                                    'addendum_utility_submetering_electricity': {
                                                            'type': 'boolean',
                                                            'empty': True,
                                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                                    },
                                                    'addendum_utility_submetering_gas': {
                                                            'type': 'boolean',
                                                            'empty': True,
                                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                                    },
                                                    'addendum_utility_submetering_water': {
                                                            'type': 'boolean',
                                                            'empty': True,
                                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                                    }
                                                }
                                        },
                                        'addendum_other': {
                                                'type': 'dict',
                                                'required': True,
                                                'schema': {
                                                    'type': 'string',
                                                    'regex': ValidationConstants.NAME_REGEX
                                                }
                                        },
                                        'addendum_other_description': {
                                                'type': 'dict',
                                                'required': True,
                                                'schema': {
                                                    'type': 'string',
                                                    'regex': ValidationConstants.NAME_REGEX
                                                }
                                        }
                                    }
                            }
                        }
        },
        'animal_addendum': {
                        'empty': True,
                        'type': 'dict',
                        'schema': {
                            'pet_additional_charges': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'pet_security_deposit': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                        },
                                        'pet_additional_rent': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                        },
                                        'pet_one_time_fee': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                        },
                                    }
                            },
                            'pet_information': {
                                'pet_name': {
                                            'type': 'list',
                                            'required': True,
                                            'schema': {
                                                    'type': 'string',
                                                    'regex': ValidationConstants.NAME_REGEX
                                                }
                                },
                                'pet_type': {
                                            'type': 'list',
                                            'required': True,
                                            'schema': {
                                                    'type': 'string',
                                                    'regex': ValidationConstants.NAME_REGEX
                                                }
                                },
                                'pet_breed': {
                                            'type': 'list',
                                            'required': True,
                                            'schema': {
                                                    'type': 'string',
                                                    'regex': ValidationConstants.NAME_REGEX
                                                }
                                },
                                'pet_color': {
                                            'type': 'list',
                                            'required': True,
                                            'schema': {
                                                    'type': 'string',
                                                    'regex': ValidationConstants.NAME_REGEX
                                                }
                                },
                                'pet_weight': {
                                            'type': 'list',
                                            'required': True,
                                            'schema': {
                                                    'type': 'string',
                                                    'regex': ValidationConstants.NUMBER_REGEX
                                                }
                                },
                                'pet_age': {
                                            'type': 'list',
                                            'required': True,
                                            'schema': {
                                                    'type': 'string',
                                                    'regex': ValidationConstants.NUMBER_REGEX
                                                }
                                },
                                'pet_license_city': {
                                            'type': 'list',
                                            'required': True,
                                            'schema': {
                                                    'type': 'string',
                                                    'regex': ValidationConstants.NAME_REGEX
                                                }
                                },
                                'pet_license_number': {
                                            'type': 'list',
                                            'required': True,
                                            'schema': {
                                                    'type': 'string',
                                                    'regex': ValidationConstants.UNIT_REGEX
                                                }
                                },
                                'pet_date_of_last_shots': {
                                            'type': 'list',
                                            'required': True,
                                            'schema': {
                                                    'type': 'string',
                                                    'regex': ValidationConstants.NUMBER_REGEX
                                                }
                                },
                                'pet_house_broken': {
                                            'type': 'list',
                                            'required': True,
                                            'schema': {
                                                    'type': 'string',
                                                    'regex': ValidationConstants.NUMBER_REGEX
                                                }
                                },
                                'pet_owners_name': {
                                            'type': 'list',
                                            'required': True,
                                            'schema': {
                                                    'type': 'string',
                                                    'regex': ValidationConstants.NUMBER_REGEX
                                                }
                                },
                            },
                            'special_provision_for_pet': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'pet_special_provisions': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                        }
                                    }
                            },
                            'emergency': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'pet_dr_name': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.NAME_REGEX
                                        },
                                        'pet_dr_address': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.STREET_ADDRESS_REGEX
                                        },
                                        'pet_dr_city': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.NAME_REGEX
                                        },
                                        'pet_dr_telephone': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.PHONE_REGEX
                                        }
                                    }
                            },
                            'pet_rules': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'pet_urinate_inside_areas': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                        },
                                        'pet_urinate_outside_areas': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                        }
                                     }
                            }
                        }
        },
        'lead_hazard': {
                'empty': True,
                'type': 'dict',
                'schema': {
                        'lead_based_paint_knowledge': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.CHARACTER_REGEX
                                        },
                        'lead_based_paint_knowledge_comments': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.CHARACTER_REGEX
                                        },
                        'lead_based_paint_reports': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.CHARACTER_REGEX
                                        },
                        'lead_based_paint_reports_comments': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.CHARACTER_REGEX
                                        }

                }
        },
        'early_lease_term': {
                        'empty': True,
                        'type': 'dict',
                        'schema': {
                            'early_termination_days_written_notice': {
                                    'type': 'integer',
                                    'regex': ValidationConstants.NUMBER_REGEX,
                                    'required': True
                            },
                            'early_termination_last_day_of_month': {
                                    'type': 'string',
                                    'regex': ValidationConstants.YEARLY_TERMINATE,
                                    'required': True
                            },
                            'early_termination_fee': {
                                    'type': 'string',
                                    'regex': ValidationConstants.AMOUNT_REGEX,
                                    'required': True
                            },
                            'early_termination_fee_due_days_before_termination': {
                                    'type': 'string',
                                    'regex': ValidationConstants.NUMBER_REGEX,
                                    'required': True
                            },
                            'early_termination_limited_to_fact': {
                                    'type': 'string',
                                    'regex': ValidationConstants.YEARLY_TERMINATE_fact,
                                    'required': True
                            },
                            'special_provision_facts': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'early_termination_special_provisions': {
                                                'type': 'string',
                                                'regex': ValidationConstants.CHARACTER_REGEX,
                                                'required': True
                                        }
                                    }
                            }
                        }

        },
        'allocation_addenda': {
                'empty': True,
                'type': 'dict',
                'schema': {
                    'national_gas_allocation_addendum': {
                                'required': True,
                                'type': 'dict',
                                'schema': {
                                    'gas_allocation_late_fee': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                    },
                                    'gas_allocation_formula': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                    },
                                    'gas_allocation_deduction_percent': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.NUMBER_REGEX
                                    },
                                    'gas_allocation_administrative_fee': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                    }
                                }
                    },
                    'government_fee_allocation_addendum': {
                                'required': True,
                                'type': 'dict',
                                'schema': {
                                    'services_govt_fees_addendum_cable_satellite': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                    },
                                    'services_govt_fees_addendum_stormwater_drainage': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                    },
                                    'services_govt_fees_addendum_trash': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                    },
                                    'services_govt_fees_addendum_street_repair': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                    },
                                    'services_govt_fees_addendum_emergency_services': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                    },
                                    'services_govt_fees_addendum_conservation_district': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                    },
                                    'services_govt_fees_addendum_inspection': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                    },
                                    'services_govt_fees_addendum_registration_license': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'allowed': ValidationConstants.BOOLEAN_CHECK
                                    },
                                    'services_govt_fees_addendum_other': {
                                                'type': 'list',
                                                'required': True,
                                                'schema': {
                                                        'type': 'string',
                                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                                 }
                                    },
                                    'services_govt_fees_addendum_other_desc': {
                                                'type': 'list',
                                                'required': True,
                                                'schema': {
                                                        'type': 'string',
                                                        'regex': ValidationConstants.CHARACTER_REGEX
                                                 }
                                    },
                                    'services_govt_fees_addendum_late_fee': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'regex': ValidationConstants.AMOUNT_REGEX
                                    },
                                    'services_govt_fees_addendum_bill_based_on': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'regex': ValidationConstants.CHARACTER_REGEX
                                    },
                                    'services_govt_fees_addendum_administrative_fee': {
                                                'type': 'boolean',
                                                'empty': True,
                                                'regex': ValidationConstants.CHARACTER_REGEX
                                    }


                                }
                    },
                    'stormwater_addendum_allocation': {
                                'required': True,
                                'type': 'dict',
                                'schema': {
                                    'stormwater_addendum_bill_based_on': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                    },
                                    'stormwater_addendum_administrative_fee': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                    }

                                }
                    },
                    'trash_removal_addendum_allocation': {
                                'required': True,
                                'type': 'dict',
                                'schema': {
                                    'trash_addendum_bill_based_on': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                    },
                                    'trash_addendum_administrative_fee': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                    },
                                    'trash_addendum_bill_late_fee': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                    }
                                }
                    },
                    'central_system_utility_allocation': {
                                'required': True,
                                'type': 'dict',
                                'schema': {
                                    'ctrl_sys_util_adden_alloc_basis': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                    },
                                    'ctrl_sys_util_adden_combo_formula_util': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                    },
                                    'ctrl_sys_util_adden_formula': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                    },
                                    'ctrl_sys_util_adden_heat_ac': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.BOOLEAN_CHECK
                                    },
                                    'ctrl_sys_util_adden_hot_water': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                    },
                                    'ctrl_sys_util_adden_monthly_avg_basis': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                    },
                                    'ctrl_sys_util_adden_monthly_avg_hot_water': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                    },
                                    'ctrl_sys_util_adden_monthly_avg_hvac': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                    },
                                    'ctrl_sys_util_adden_submetered_formula_util': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                    }

                                }
                    }

                }
        },
        'misc_addenda': {
                        'empty': True,
                        'type': 'dict',
                        'schema': {
                            'resident_electronic_payment': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                            'resident': {
                                                    'type': 'list',
                                                    'required': True,
                                                    'schema': {
                                                        'type': 'string',
                                                        'regex': ValidationConstants.NAME_REGEX
                                                    }
                                             },
                                            'resident_rent': {
                                                    'type': 'list',
                                                    'required': True,
                                                    'schema': {
                                                        'type': 'string',
                                                        'regex': ValidationConstants.AMOUNT_REGEX
                                                    }
                                             },
                                            'electronic_special_provision': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.CHARACTER_REGEX
                                            }
                                      }
                            },
                            'enclosed_garage': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'garage_addendum_carport_provided': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'garage_addendum_garage_space_no': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.AMOUNT_REGEX
                                        },
                                        'garage_addendum_carport_space_no': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.AMOUNT_REGEX
                                        },
                                        'garage_addendum_storage_unit_no': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.AMOUNT_REGEX
                                        },
                                        'garage_addendum_opener_fine': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.AMOUNT_REGEX
                                        },
                                        'garage_addendum_garage_key': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'garage_addendum_garage_opener': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'garage_addendum_garage_or_carport_provided': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'garage_addendum_garage_provided': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                    }
                            },
                            'legal_description': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'legal_description_of_unit': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.CHARACTER_REGEX
                                        }
                                    }
                            },
                            'move_out_notice': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'addendum_move_out_days_notice': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.NUMBER_REGEX
                                        }
                                    }
                            },
                            'no_smoking': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'no_smoking_addendum_smoking_permitted_balcony': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'no_smoking_addendum_smoking_permitted_outside': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'no_smoking_addendum_smoking_areas': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.CHARACTER_REGEX
                                        },
                                        'no_smoking_addendum_smoking_distance': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.NUMBER_REGEX
                                        }
                                    }
                            },
                            'patio_yard_maintenance': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'party_responsible_for_lawn_mowing': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'party_responsible_for_lawn_watering': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'party_responsible_for_lawn_trash': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'party_obligated_to_fertilize': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        }
                                    }
                            },
                            'satellite_dish': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'satellite_addendum_no_dishes': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.NUMBER_REGEX
                                        },
                                        'satellite_addendum_insurance': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.AMOUNT_REGEX
                                        },
                                        'satellite_addendum_security_deposit': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.AMOUNT_REGEX
                                        },
                                        'satellite_addendum_security_deposit_days': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.NUMBER_REGEX
                                        },
                                    }
                            },
                            'trash_removal_recycle': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'trash_addendum_bill_late_fee': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.AMOUNT_REGEX
                                        },
                                        'addendum_trash_removal_recycling_flat_fee': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.AMOUNT_REGEX
                                        },
                                        'trash_addendum_administrative_fee_flat': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.AMOUNT_REGEX
                                        },
                                    }
                            },
                            'carrying_handguns_onsite': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'gun_no_conceal_area': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'gun_no_conceal_office': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'gun_no_conceal_property': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'gun_no_conceal_rooms': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'gun_no_open_carry_area': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'gun_no_open_carry_office': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'gun_no_open_carry_property': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'gun_no_open_carry_rooms': {
                                                    'type': 'boolean',
                                                    'empty': True,
                                                    'allowed': ValidationConstants.BOOLEAN_CHECK
                                        }
                                    }
                            },
                            'short_term_lease': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'short_lease_special_provisions': {
                                                    'type': 'string',
                                                    'empty': True,
                                                    'regex': ValidationConstants.CHARACTER_REGEX
                                        }
                                    }
                            },
                            'install_dryer': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'dryer_install': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        },
                                        'washer_install': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        }
                                    }
                            }
                        }
        },
        'remote_card_code': {
                'empty': True,
                'type': 'dict',
                'schema': {
                    'remote_control_gate_access': {
                            'required': True,
                            'type': 'dict',
                            'schema': {
                                'remote_card_code_addendum_remote': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                    },
                                'remote_card_code_addendum_add_card_fee': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'remote_card_code_addendum_card': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'remote_card_code_addendum_add_remote_fee': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'remote_card_code_addendum_code': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                }
                            }
                    },
                    'damaged_lust_cards': {
                        'required': True,
                        'type': 'dict',
                        'schema': {
                            'remote_card_code_addendum_lost_remote': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                            },
                            'remote_card_code_addendum_replace_remote_fee': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                            },
                            'remote_card_code_addendum_lost_remote_deduct': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                            },
                            'remote_card_code_addendum_lost_card': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                            },
                            'remote_card_code_addendum_replace_card_fee': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                            },
                            'remote_card_code_addendum_lost_card_deduct': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                            },
                            'remote_card_code_addendum_code_change': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                            }
                        }
                    }
                }
        },
        'electric_water_wastewater': {
                'empty': True,
                'type': 'dict',
                'schema': {
                    'electronic_subterming': {
                            'required': True,
                            'type': 'dict',
                            'schema': {
                                'electric_service_reconnect_fee': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'addendum_utility_submetering': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'electric_service_allocation_unit_square_feet_percent': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.NUMBER_REGEX
                                },
                                'electric_service_estimated_percent_use': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'electric_service_allocation_method': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.NUMBER_REGEX
                                }
                            }
                    },
                    'water_waste_water_subterming': {
                                'required': True,
                                'type': 'dict',
                                'schema': {
                                    'submeter_average_monthly_bill': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                    },
                                    'submeter_lowest_monthly_bill': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                    },
                                    'submeter_highest_monthly_bill': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                    },
                                    'submeter_water_service_fee': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.NUMBER_REGEX
                                    },
                                    'submeter_water_consumption_from_date': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.DATE_REGEX
                                    },
                                    'submeter_water_consumption_to_date': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.DATE_REGEX
                                    },
                                    'water_allocation_bill_date': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.DATE_REGEX
                                    },
                                    'tceq_water_allocation_method': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.CHARACTER_REGEX
                                    }
                                }
                    }
                }
        },
        'rent_concessions': {
                'empty': True,
                'type': 'dict',
                'schema': {
                    'rent_concessions_other_discount': {
                            'required': True,
                            'type': 'dict',
                            'schema': {
                                'addendum_rent_concession_one_time': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'addendum_rent_concession_one_time_amount': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'addendum_rent_concession_one_time_months': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                },
                                'addendum_rent_concession_special_provisions': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                },
                                'addendum_rent_concession_monthly_discount': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'addendum_rent_concession_discounted_months': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.NUMBER_REGEX
                                },
                                'addendum_rent_concession_amount': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                }
                            }
                    }
                }
        },
        'intrusion_alarm': {
                'empty': True,
                'type': 'dict',
                'schema': {
                    'alarm': {
                            'required': True,
                            'type': 'dict',
                            'schema': {
                                'alarm_required': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                },
                                'alarm_permit_required_to_activate': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                },
                                'alarm_permit_activation_contact': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.PHONE_REGEX
                                },
                                'alarm_instructions_attached': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                },
                                'alarm_required_company': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                },
                                'alarm_resident_chooses_company': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                },
                                'alarm_repair_contact': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                },
                                'alarm_repairs_paid_by': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                },
                                'alarm_company_required_to_activate': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                },
                                'alarm_maintainer': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                }
                            }
                    }
                }
        },
        'additional_provisions': {
                'empty': True,
                'type': 'dict',
                'schema': {
                    'special_provisions': {
                            'required': True,
                            'type': 'dict',
                            'schema': {
                                'additional_special_provisions': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                }
                            }
                    },
                    'rental_of_dwelling': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'per_person_bedroom_sharing': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                        },
                                        'per_person_max_sharing_common_areas': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.NUMBER_REGEX
                                        },
                                        'per_person_transfer_fee': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.AMOUNT_REGEX
                                        }
                                    }
                    },
                    'activities_addendum': {
                            'required': True,
                            'type': 'dict',
                            'schema': {
                                    'construction_special_provisions': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                    }
                            }
                    }

                }
        },
        'renter_insurance': {
                'empty': True,
                'type': 'dict',
                'schema': {
                    'renter_liability': {
                            'required': True,
                            'type': 'dict',
                            'schema': {
                                'renters_insurance_liability_limit': {
                                            'type': 'string',
                                            'required': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                },
                                'renters_insurance_default_fee': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                }
                            }
                    }
                }
        },
        'lease_guaranty': {
                'empty': True,
                'type': 'dict',
                'schema': {
                    'guarantor_last_date_for_renewal': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.DATE_REGEX
                    },
                    'guarantor_length_of_obligations': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                    },
                    'contract_guaranty': {
                                    'required': True,
                                    'type': 'dict',
                                    'schema': {
                                        'addendum_lease_contract_guaranty': {
                                            'type': 'boolean',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                        }
                                    }
                    }
                }
        },
        'summary_of_key_information': {
                'empty': True,
                'type': 'dict',
                'schema': {
                    'summary_information': {
                            'required': True,
                            'type': 'dict',
                            'schema': {
                                'address': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.STREET_ADDRESS_REGEX
                                },
                                'unit_number': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.UNIT_REGEX
                                },
                                'lease_begin_date': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.DATE_REGEX
                                },
                                'lease_end_date': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.DATE_REGEX
                                },
                                'days_required_for_notice_of_lease_termination': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.NUMBER_REGEX
                                },
                                'days_prorated': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.NUMBER_REGEX
                                },
                                'security_deposit': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'security_deposit_includes_animal_deposit': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'security_deposit_refund_check_payable': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.CHARACTER_REGEX
                                },
                                'security_deposit_refund_one_check_mailed_to': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.EMAIL_REGEX
                                },
                                'number_of_apartment_keys': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.NUMBER_REGEX
                                },
                                'number_of_mail_keys': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.NUMBER_REGEX
                                },
                                'number_of_other_keys': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.NUMBER_REGEX
                                },
                                'addendum_rent_concession': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.NUMBER_REGEX
                                },
                                'pay_rent_address': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.URL_REGEX
                                },
                                'pay_rent_at_online_site': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'pay_rent_on_site': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'garage_cost_included_in_rent': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'carport_cost_included_in_rent': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'other_cost_included_in_rent': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'storage_cost_included_in_rent': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'washer_dryer_cost_included_in_rent': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'utilities_gas': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'utilities_water': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'utilities_trash': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'utilities_electricity': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'utilities_cable_tv': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'utilities_master_antenna': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'utilities_internet': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'utilities_stormwater_drainage': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'utilities_other': {
                                        'type': 'string',
                                        'empty': True,
                                        'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'renters_insurance_requirement': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.CHARACTER_REGEX
                                },
                                'rent_due_date': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.NUMBER_REGEX
                                },
                                'prorated_rent': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.NUMBER_REGEX
                                },
                                'rent': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'late_charge_initial_charge': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'late_charge_percentage_of_rent': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.NUMBER_REGEX
                                },
                                'late_charge_daily_charge': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'late_charge_daily_percent_of_rent': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.NUMBER_REGEX
                                },
                                'returned_check_charge': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'pet_additional_rent': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'pet_charge_initial_charge': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'pet_charge_daily_charge': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'monthly_pest_control_rent': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'monthly_trash_rent': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'electric_transfer_fee': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.AMOUNT_REGEX
                                },
                                'special_provisions': {
                                        'type': 'string',
                                        'empty': True,
                                        'regex': ValidationConstants.CHARACTER_REGEX
                                }
                            }
                    }
                }
        },
        'covid-19': {
                'empty': True,
                'type': 'dict',
                'schema': {
                    'notice_of_temporary_waiver': {
                                'required': True,
                                'type': 'dict',
                                'schema': {
                                    'waiver_period_start_date': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.DATE_REGEX
                                    },
                                    'waiver_period_end_date': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.DATE_REGEX
                                    },
                                    'waiver_period_rent_due_date': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.NUMBER_REGEX
                                    },
                                    'waiver_phone_contact': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.PHONE_REGEX
                                    },
                                    'waiver_email_contact': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.EMAIL_REGEX
                                    }
                                }
                    },
                    'payment_plan_agreement': {
                            'required': True,
                            'type': 'dict',
                            'schema': {
                                'pay_plan_lease_signed_date': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.DATE_REGEX
                                },
                                'pay_plan_lease_signed_year': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.YEAR_REGEX
                                },
                                'pay_plan_due_current_month': {
                                            'type': 'string',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'pay_plan_due_next_month': {
                                            'type': 'string',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'pay_plan_due_time_period': {
                                            'type': 'string',
                                            'empty': True,
                                            'allowed': ValidationConstants.BOOLEAN_CHECK
                                },
                                'pay_plan_due_time_period_description': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.CHARACTER_REGEX
                                },
                                'pay_plan_due_date': {
                                        'type': 'list',
                                        'required': True,
                                        'schema': {
                                            'type': 'string',
                                                'regex': ValidationConstants.DATE_REGEX
                                        }
                                    },
                                'pay_plan_amount': {
                                        'type': 'list',
                                        'required': True,
                                        'schema': {
                                            'type': 'string',
                                                'regex': ValidationConstants.DATE_REGEX
                                        }
                                    }

                            }
                    },
                    'virus_warning_and_waiver': {
                            'required': True,
                            'type': 'dict',
                            'schema': {
                                'virus_waiver_signed_date': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.DATE_REGEX
                                },
                                'virus_waiver_signed_year': {
                                            'type': 'string',
                                            'empty': True,
                                            'regex': ValidationConstants.YEAR_REGEX
                                }
                            }
                    }
                }
        },
        'custom_forms': {
            'type': 'dict'
        }
    },
    Schema.DELETE_LEASE: {
        'leaseId': {
                'required': True,
                'regex': ValidationConstants.NUMBER_REGEX,
                'type': ['string', 'integer']
        }
    },
    Schema.CREATE_ESIGNATURE: {
        'eSignatureData': {
            'type': 'dict',
            'required': True,
            'schema': {
                'notificationURL': {
                    'type': 'string',
                    'empty': True,
                    'regex': ValidationConstants.URL_REGEX
                },
                'sendNotifications': {
                    'type': 'boolean'
                },
                'redirectURL': {
                    'type': 'string',
                    'empty': True,
                    'regex': ValidationConstants.URL_REGEX
                },
                'redirectButtonText': {
                    'type': 'string',
                    'empty': True,
                    'regex': ValidationConstants.CHARACTER_REGEX
                },
                'eSignatureLifeSpan': {
                    'type': 'string',
                    'empty': True,
                    'regex': ValidationConstants.NUMBER_REGEX
                },
                'forms': {
                    'type': 'list',
                    'required': True,
                    'schema': {
                        'type': 'dict',
                        'schema': {
                            'form': {
                                'type': 'string',
                                'required': True
                            },
                            'language': {
                                'type': 'string',
                                'required': True,
                                'allowed': ['english', 'spanish']
                            }
                        }
                    }
                },
                'owner': {
                    'type': 'dict',
                    'empty': True,
                    'schema': {
                        'name': {
                            'type': 'string',
                            'empty': True,
                            'regex': ValidationConstants.NAME_REGEX
                        },
                        'email': {
                            'type': 'string',
                            'empty': True,
                            'regex': ValidationConstants.EMAIL_REGEX
                        },
                        'phone': {
                            'type': 'string',
                            'empty': True,
                            'regex': ValidationConstants.PHONE_REGEX
                        }
                    },
                    'signers': {
                        'type': 'list',
                        'empty': True,
                        'schema': {
                            'type': 'dict',
                            'schema': {
                                'email': {
                                    'empty': True,
                                    'type': 'string',
                                    'regex': ValidationConstants.EMAIL_REGEX,
                                    'excludes': 'phone'
                                },
                                'phone': {
                                    'empty': True,
                                    'type': 'string',
                                    'regex': ValidationConstants.PHONE_REGEX,
                                    'excludes': 'email'
                                }
                            }

                        }
                    }
                }
            }

        }
    }
}

