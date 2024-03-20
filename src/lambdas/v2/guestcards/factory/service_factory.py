from abstract.service_interface import ServiceInterface
from utils.service_enum import ServiceType, PartnerSystem
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
    def get_service(service_type_name: str, partner_system: str) -> ServiceInterface:
        # Validate service type using enum constructor
        try:
            service_type = ServiceType(service_type_name.lower())
            partner_system = PartnerSystem(partner_system.lower()) if partner_system else None
        except ValueError:
            raise Exception(f"Unsupported service type for GuestCards: {service_type_name}")
        
        # Return service
        if service_type == ServiceType.ENTRATA:
            return EntrataService()
        elif service_type == ServiceType.FUNNEL:
            return FunnelService()
        elif service_type == ServiceType.REALPAGE and partner_system == PartnerSystem.REALPAGE_ONESITE:
            return RealPageService()
        elif service_type == ServiceType.RESMAN:
            return ResManService()
        elif service_type == ServiceType.YARDI:
            return YardiService()
        elif service_type == ServiceType.REALPAGE and partner_system in [PartnerSystem.REALPAGE_ILM, PartnerSystem.REALPAGE_L2L]:
            return RealPageILMService()
        elif service_type == ServiceType.SPHEREXX:
            return SpherexxService()
        elif service_type == ServiceType.MRI:
            return MRIService()


        