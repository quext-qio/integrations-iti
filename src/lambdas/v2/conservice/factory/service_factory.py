from abstract.service_interface import ServiceInterface
from utils.shared.service_enum import ServiceType
from services.charges_code_service import ChargesCodeService
from services.properties_service import PropertiesService
from services.add_charges_service import AddChargesService
from services.urls_date_required_services import URLDateRequiredServices
from services.invalid_action_service import InvalidActionService

class ServiceFactory:
    @staticmethod
    def get_service(service_type_name: str) -> ServiceInterface:
        # Validate service type using enum constructor
       
        service_type = service_type_name.lower()
       
        # Return service
        if service_type == ServiceType.CHARGES_ENDPOINTS.value:
            return ChargesCodeService()
        elif service_type == ServiceType.ADD_CHARGES.value:
            return AddChargesService()
        elif service_type == ServiceType.PROPERTIES.value:
            return PropertiesService()
        elif service_type in ServiceType.URLS_DATE_REQUIRED.value:
            return URLDateRequiredServices()
        else:
            return InvalidActionService()
        
            
        