from abstract.service_interface import ServiceInterface
from utils.service_enum import ServiceType
from services.entrata_service import EntrataService
from services.funnel_service import FunnelService
from services.realpage_service import RealPageService
from services.resman_service import ResManService
from services.yardi_service import YardiService
from services.realpage_ilm_service import RealPageILMService
from services.spherexx_service import SpherexxService
from services.mri_service import MRIService

class ServiceFactory:
    @staticmethod
    def get_service(service_type_name: str) -> ServiceInterface:
        # Validate service type using enum constructor
        try:
            service_type = ServiceType(service_type_name.lower())
        except ValueError:
            raise Exception(f"Unsupported service type for GuestCards: {service_type_name}")
        
        # Return service
        if service_type == ServiceType.ENTRATA:
            return EntrataService()
        elif service_type == ServiceType.FUNNEL:
            return FunnelService()
        elif service_type == ServiceType.REALPAGE:
            return RealPageService()
        elif service_type == ServiceType.RESMAN:
            return ResManService()
        elif service_type == ServiceType.YARDI:
            return YardiService()
        elif service_type == ServiceType.REALPAGEILM or service_type == ServiceType.REALPAGEL2L:
            return RealPageILMService()
        elif service_type == ServiceType.SPHEREXX:
            return SpherexxService()
        elif service_type == ServiceType.MRI:
            return MRIService()


        