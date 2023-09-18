from abstract.service_interface import ServiceInterface
from utils.shared.service_enum import ServiceType
from services.charge_codes_service import ChargeCodesService
from services.add_charges_service import AddChargesService
from services.lease_charges import LeaseChargesService
from services.tenants import TenantsService 
from services.properties_service import PropertiesService
from services.recurring_transactions_service import RecurringTransactionsService
from services.invalid_action_service import InvalidActionService

class ServiceFactory:
    @staticmethod
    def get_service(service_type_name: str) -> ServiceInterface:
        # Validate service type using enum constructor
        try:
            service_type = ServiceType(service_type_name.lower())
        except Exception as e:
            service_type = ServiceType.INVALID_ACTION
            
        # Return service
        if service_type == ServiceType.CHARGE_CODES:
            return ChargeCodesService()
        elif service_type == ServiceType.LEASE_CHARGES:
            return LeaseChargesService()
        elif service_type == ServiceType.TENANTS:
            return TenantsService()
        elif service_type == ServiceType.ADD_CHARGES:
            return AddChargesService()
        elif service_type == ServiceType.GET_PROPERTIES:
            return PropertiesService()
        elif service_type == ServiceType.GET_RECURRING_TRANSACTIONS:
            return RecurringTransactionsService()
        else:
            return InvalidActionService()
        
            
        