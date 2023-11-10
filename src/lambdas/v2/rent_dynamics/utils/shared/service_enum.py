from enum import Enum

# Validate the values in this enum are the same of IPS service names
class ServiceType(Enum):
    INVALID_ACTION = ""
    CHARGE_CODES = "chargecodes"
    UNITS_AND_FLOOR_PLANS = "unitsandfloorplans"
    RESIDENTS = "residents"
    TRANSACTIONS = "transactions"
    CUSTOMER_EVENTS = "customerevents"
    