from abstract.service_interface import ServiceInterface
from utils.shared.service_enum import ServiceType
from services.charge_codes_service import ChargeCodesService
from services.units_and_floor_plans_service import UnitsAndFloorPlantsService
from services.residents_service import ResidentsService
from services.prospects_service import ProspectsService
from services.properties_service import PropertiesService
from services.transactions_service import TransactionsService
from services.customer_events_service import CustomerEventsService


class ServiceFactory:
    @staticmethod
    def get_service(service_type_name: str) -> ServiceInterface:
        # Validate service type using enum constructor
        try:
            service_type = ServiceType(service_type_name.lower())
        except ValueError:
            raise Exception(f"Unsupported service type for Rent Dynamics: {service_type_name}")
        
        # Return service
        if service_type == ServiceType.CHARGE_CODES:
            return ChargeCodesService()
        elif service_type == ServiceType.UNITS_AND_FLOOR_PLANS:
            return UnitsAndFloorPlantsService()
        elif service_type == ServiceType.RESIDENTS:
            return ResidentsService()
        elif service_type == ServiceType.PROSPECTS:
            return ProspectsService()
        elif service_type == ServiceType.PROPERTIES:
            return PropertiesService()
        elif service_type == ServiceType.TRANSACTIONS:
            return TransactionsService()
        elif service_type == ServiceType.CUSTOMER_EVENTS:
            return CustomerEventsService()
        
            
        