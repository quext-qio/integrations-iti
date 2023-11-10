from abstract.service_interface import ServiceInterface
from utils.shared.service_enum import ServiceType
from services.charge_codes_service import ChargeCodesService
from services.units_and_floor_plans_service import UnitsAndFloorPlantsService
from services.residents_service import ResidentsService
from services.transactions_service import TransactionsService
from services.customer_events_service import CustomerEventsService
from services.invalid_action_service import InvalidActionService

class ServiceFactory:
    @staticmethod
    def get_service(service_type_name: str, logger) -> ServiceInterface:
        # Validate service type using enum constructor
        try:
            service_type = ServiceType(service_type_name.lower())
        except Exception as e:
            logger.error(f"Invalid service type: {service_type_name}")
            service_type = ServiceType.INVALID_ACTION
            
        # Return service
        if service_type == ServiceType.CHARGE_CODES:
            logger.info(f"Factory Response: ChargeCodesService")
            return ChargeCodesService()
        elif service_type == ServiceType.UNITS_AND_FLOOR_PLANS:
            logger.info(f"Factory Response: UnitsAndFloorPlantsService")
            return UnitsAndFloorPlantsService()
        elif service_type == ServiceType.RESIDENTS:
            logger.info(f"Factory Response: ResidentsService")
            return ResidentsService()
        elif service_type == ServiceType.TRANSACTIONS:
            logger.info(f"Factory Response: TransactionsService")
            return TransactionsService()
        elif service_type == ServiceType.CUSTOMER_EVENTS:
            logger.info(f"Factory Response: CustomerEventsService")
            return CustomerEventsService()
        else:
            logger.info(f"Factory Response: InvalidActionService")
            return InvalidActionService()
        
            
        