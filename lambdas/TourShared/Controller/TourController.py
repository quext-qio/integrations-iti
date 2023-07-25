from DataPushPullShared.Utilities.DataController import DataValidation, Schema
from TourShared.Model.Data_Model import TourAvailabilityData
from TourShared.Utilities.Data_Validation import DataValidation as TourDataValidation
from ExceptionHandling.Model.Exceptions import ValidationError
from ExceptionHandling.Utilities.ErrorCode import ErrorCode
from VendorShared.Controller.VendorResolverController import VendorRouter
from VendorShared.Model.ServiceRequest import ServiceRequest
from DataPushPullShared.Utilities.Convert import Convert
from bunch import bunchify
from Utils import CustomLogger

logging = CustomLogger.logger


class TourController:
    """
    ResidentController handles the resident related business operations by
    communicating with necessary services based on the request given.
    """

    def __validate(self, service_request: ServiceRequest):
        """
        Perform the basic validation on the request input for performing operations on the residents

        Parameters
        ----------
        service_request : ServiceRequest
            The input request
        """
        _isValid, _errors = DataValidation.schema(Schema.TOUR_AVAILABILITY, service_request.request.payload)
        
        if _errors:
            logging.info("Validation_error: {}".format(_errors))
            raise ValidationError(ErrorCode.ERROR_DATA_0001, _errors)

    def get_tour_availabilities(self, service_request: ServiceRequest):
        """
        Call the IPS service and resolve the vendor based the IPS response and
        get the tour availabilities from the vendor

        Parameters
        ----------
        service_request : ServiceRequest
            The input request
        """

        # validating input request
        logging.info('get tour availabilities controller')
        self.__validate(service_request)

        # Adding PlatformData
        service_request.payload.update({"customerUUID": service_request.request.payload['platformData']['customerUUID'],
                                        "communityUUID": service_request.request.payload['platformData'][
                                            'communityUUID']})

        # Validating input request data
        tour_availability_data = TourAvailabilityData()
        tour_availability_data.fromDate = service_request.request.payload["timeData"]["fromDate"].split("T")[0]
        tour_availability_data.toDate = service_request.request.payload["timeData"]["toDate"].split("T")[0]
        logging.info("get tour availabilities dates %s" %vars(tour_availability_data))

        _isValid, _errors = TourDataValidation.validate_schedule_availability_formData(tour_availability_data)
        
        if _errors:
            logging.info("Validation_error".format(_errors))
            raise ValidationError(ErrorCode.ERROR_DATA_0001, _errors)

        # Resolving Vendor Gateway
        vendor_gateway_controller = VendorRouter().resolve_vendor(service_request)

        # Getting tour availabilities
        tour_availabilities = vendor_gateway_controller.get_tour_availabilities(service_request, tour_availability_data)
        logging.info('tour_availability: {}'.format(vars(tour_availabilities)))
        utc_date_list = Convert.get_utc(tour_availabilities.availableTimes, 'UTC')
        tour_availabilities.availableTimes = utc_date_list
        logging.info("utc_date_list: {}".format(utc_date_list))
        logging.info("Successfully got the tour schedules from the vendor")
        return tour_availabilities

    def book_tour_appointment(self, service_request: ServiceRequest):
        """
        Call the IPS service and resolve the vendor based the IPS response and
        book the tour appointment to the vendor

        Parameters
        ----------
        service_request : ServiceRequest
            The input request
        """

        # validating input request
        logging.info('Entering tour appointment')
        self.__validate(service_request)
        form_data = bunchify(service_request.request.payload)

        # Resolving Vendor Gateway
        vendor_gateway_controller = VendorRouter().resolve_vendor(service_request)
        
        # Post book_tour_appointments
        book_tour_response = vendor_gateway_controller.book_tour_appointment(service_request, form_data.appointmentData)
        logging.info("Booked the tour appointment with the vendor")
        return book_tour_response
