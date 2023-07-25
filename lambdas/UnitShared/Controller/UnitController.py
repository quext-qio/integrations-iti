# import logging
from DataPushPullShared.Utilities.DataController import DataValidation, Schema,QuextIntegrationConstants
from ExceptionHandling.Model.Exceptions import ValidationError
from ExceptionHandling.Utilities.ErrorCode import ErrorCode
from VendorShared.Controller.VendorResolverController import VendorRouter
from VendorShared.Model.ServiceRequest import Auth, ServiceRequest
from ExceptionHandling.Utilities.ErrorCode import ErrorCode
from ExceptionHandling.Model.Exceptions import ValidationError
from UnitShared.Utils.Utils import PostResponse
from Utils import CustomLogger
from UnitShared.Model.UnitResponseV2 import UnitErrorResponse

logging = CustomLogger.logger


class UnitController:
    """
        Handles the Generic validation and returns the 
        respective vendors Object(Resman,Realpage)
    """

    def __validate(self, service_request: ServiceRequest):
        """
        Validates the input payload and returns the Boolean Value

        Parameters
        ----------
        service_request: ServiceRequest
        """

        isvalid, _error = DataValidation.schema(Schema.UNIT_AVAILABILITY, service_request.request.payload)

        if (_error):
            raise ValidationError(ErrorCode.ERROR_HTTP_0001, _error)
        
    def __build_response(self, servicerequest: ServiceRequest, response: dict, partner_name: str):
        """ Returns the post Response json by using the Response dict

        Args:
            servicerequest (ServiceRequest): ServiceRequest Object
            response (dict): Response to the end user

        Returns:
            _type_: Object
        """
        response_obj = PostResponse(servicerequest, response, partner_name)
        return response_obj.build_response()          

    def get_unit_availability(self, service_request: ServiceRequest):
        """
        Returns the Units Endpoint results by resolving the Vendor using the factory design
        pattern and implement the respective third party endpoint. 

        Parameters
        ----------
        service_request: ServiceRequest Object
        """
        self.__validate(service_request=service_request)

        # Adding PlatformData
        service_request.payload.update({"customerUUID": service_request.request.payload['platformData']['customerUUID'],
                                        "communityUUID": service_request.request.payload['platformData'][
                                            'communityUUID']})

        router = VendorRouter()
        outgoing_channel = router.get_communities_info(service_request)
        
        data_list = []
        error = []
        error_dict = {}
        
        for channel in outgoing_channel:
            try:
                authconfig = channel.security
                authconfig.update(channel.platformdata)
                service_request.auth = Auth(authconfig)
                logging.info("authentication built successfully")
                _response = channel.partner_object.get_unit_availability(service_request)
                final_response = self.__build_response(servicerequest = service_request,response=_response, partner_name = channel.partner_name)
                data_list.append(final_response)
            except Exception as e:
                logging.info("Handling exception in unit controller")
                error_obj = UnitErrorResponse()
                logging.info(e)
                error_obj.community_id = channel.community_id
                error_obj.partner_name = channel.partner_name
                error_obj.error_message = e
                error.append(dict(error_obj))
       
        error_dict[QuextIntegrationConstants.ERROR] = error
        return data_list, error_dict
    