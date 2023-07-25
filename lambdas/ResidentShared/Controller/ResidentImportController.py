from DataPushPullShared.Utilities.DataController import DataValidation, Schema
from ExceptionHandling.Model.Exceptions import ValidationError
from ExceptionHandling.Utilities.ErrorCode import ErrorCode
from VendorShared.Controller.VendorResolverController import VendorRouter
from VendorShared.Model.ServiceRequest import ServiceRequest


class ResidentImportController:
    """
    ResidentImportController handles the resident related business operations by
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
        _isValid, _errors = DataValidation.schema(Schema.PLATFORM_DATA, service_request.payload)
        if _errors:
            raise ValidationError(ErrorCode.ERROR_DATA_0001, _errors)

    def get_residents(self, service_request: ServiceRequest):
        """
        Call the IPS service and resolve the vendor based the IPS response

        Parameters
        ----------
        service_request : ServiceRequest
            The input request
        """

        # validating input request
        self.__validate(service_request)
        # Resolving Vendor Gateway
        vendor_gateway_controller = VendorRouter().resolve_vendor(service_request)
        # Getting residents
        residents = vendor_gateway_controller.get_residents(service_request)
        return residents
