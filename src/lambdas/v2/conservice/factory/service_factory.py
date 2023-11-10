from abstract.service_interface import ServiceInterface
from utils.shared.service_enum import ServiceType
from services.charges_code_service import ChargesCodeService
from services.properties_service import PropertiesService
from services.add_charges_service import AddChargesService
from services.urls_date_required_services import URLDateRequiredServices
from services.invalid_action_service import InvalidActionService

class ServiceFactory:
    @staticmethod
    def get_service(service_type_name: str, logger) -> ServiceInterface:
        # Validate service type using enum constructor
       
        service_type = service_type_name.lower()
       
        # Return service
        if service_type == ServiceType.CHARGES_ENDPOINTS.value:
            logger.info(f"Factory response: ChargesCodeService")
            return ChargesCodeService()
        elif service_type == ServiceType.ADD_CHARGES.value:
            logger.info(f"Factory response: AddChargesService")
            return AddChargesService()
        elif service_type == ServiceType.PROPERTIES.value:
            logger.info(f"Factory response: PropertiesService")
            return PropertiesService()
        elif service_type in ServiceType.URLS_DATE_REQUIRED.value:
            logger.info(f"Factory response: URLDateRequiredServices")
            return URLDateRequiredServices()
        else:
            logger.warning(f"Factory response: InvalidActionService")
            return InvalidActionService()
        
            
        