from abc import abstractmethod, ABC

from TourShared.Model.Data_Model import TourAvailabilityData
from VendorShared.Model.ServiceRequest import ServiceRequest


class VendorGatewayController(ABC):
    """
    VendorGatewayController plays as abstract class for all third party vendors and responsible for collecting
    data based on the request
    """

    @abstractmethod
    def get_residents(self, service_request: ServiceRequest):
        """
        Get residents information
        """
        pass

    @abstractmethod
    def get_leases(self, service_request: ServiceRequest):
        """
        Get Leasing information
        """
        pass

    @abstractmethod
    def get_locations(self, service_request: ServiceRequest):
        """
        Get location information
        """
        pass

    @abstractmethod
    def get_unit_availability(self, service_request: ServiceRequest):
        """
        Get unit information
        """
        pass

    @abstractmethod
    def post_guestcards(self, service_request: ServiceRequest):
        """
        Get guest card information
        """
        pass

    @abstractmethod
    def get_tour_availabilities(self, service_request: ServiceRequest, tour_availability_data: TourAvailabilityData):
        """
        Get tour available information
        """
        pass

    #@abstractmethod
    #def book_tour_appointment(self, service_request: ServiceRequest, appointmentData):
    #    """
    #    Post book tour appointment
    #    """
    #    pass
