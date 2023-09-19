from enum import Enum

# Validate the values in this enum are the same of IPS service names
class ServiceType(Enum):
    CHARGES_ENDPOINTS = 'get-charge-codes'
    ADD_CHARGES = 'add-charges'
    PROPERTIES = "get-properties"
    URLS_DATE_REQUIRED = ['tenants', 'get-recurring-transactions', 'lease-charges']
    INVALID_ACTION = ""
    