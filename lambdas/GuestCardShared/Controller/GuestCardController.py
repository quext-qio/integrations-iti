from VendorShared.Model.ServiceRequest import ServiceRequest
from VendorShared.Controller.VendorResolverController import VendorRouter
from DataPushPullShared.Utilities.DataController import DataValidation, Schema
from VendorShared.Controller.VendorResolverController import VendorRouter
from VendorShared.Model.ServiceRequest import ServiceRequest
from ExceptionHandling.Utilities.ErrorCode import ErrorCode
from ExceptionHandling.Model.Exceptions import ValidationError
from GuestCardShared.Utils.GuestCardResponse import generate_comments
from Utils import CustomLogger

logging = CustomLogger.logger



class GuestCardController:
    """
        GuestCardController handles the guest card related business operations by
        communicating with the necessary services based on the request given
    """

    def __validate(self, service_request: ServiceRequest):
        """         
        Validates the input payload(communityUUId,customerUUId) 
        and returns the Boolean Value

        Parameters
        ----------
        service_request: ServiceRequest object
        """
        isvalid, _error = DataValidation.schema(Schema.GUEST_CARDS, service_request.request.payload)

        if _error:
            raise ValidationError(ErrorCode.ERROR_HTTP_0001, _error)

    def post_guestcards(self, service_request: ServiceRequest):
        """
        Call the IPS service and resolve the vendor based on the IPS response

        Parameters
        ----------
        service_request : ServiceRequest
            The input request
        """

        # validating input request
        self.__validate(service_request=service_request)

        # Adding PlatformData
        service_request.payload.update({"customerUUID": service_request.request.payload['platformData']['customerUUID'],
                                        "communityUUID": service_request.request.payload['platformData'][
                                            'communityUUID']})

        # resolving vendor gateway
        vendor_gateway_controller = VendorRouter().resolve_vendor(service_request)
        logging.info('Vendor resolved successfully')
        generate_comment = generate_comments(service_request)
        logging.info("Generated comments:".format(generate_comment))
        service_request.__setattr__('guest_card_comment', generate_comment)
        # getting guestcards
        guestcards = vendor_gateway_controller.post_guestcards(service_request)

        return guestcards
