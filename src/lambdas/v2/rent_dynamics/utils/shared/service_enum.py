from enum import Enum

# Validate the values in this enum are the same of IPS service names
class ServiceType(Enum):
    UNITS_AND_FLOOR_PLANS = "unitsandfloorplans"
    RESIDENTS = "residents"
    PROSPECTS = "prospects"
    CHARGE_CODES = "chargecodes"
    PROPERTIES = "properties"
    TRANSACTIONS = "transactions"
    CUSTOMER_EVENTS = "customerevents"
    