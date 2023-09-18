from enum import Enum

# Validate the values in this enum are the same of IPS service names
class ServiceType(Enum):
    TENANTS = "tenants"
    GET_RECURRING_TRANSACTIONS = "get-recurring-transactions"
    LEASE_CHARGES = "lease-charges"
    ADD_CHARGES = "add-charges"
    GET_PROPERTIES = "get-properties"
    CHARGE_CODES = "get-charge-codes"
    