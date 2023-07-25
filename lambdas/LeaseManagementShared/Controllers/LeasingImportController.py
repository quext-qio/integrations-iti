from DataPushPullShared.Utilities.DataController import DataValidation, Schema
from VendorShared.Controller.VendorResolverController import VendorRouter
from VendorShared.Model.ServiceRequest import ServiceRequest
from ExceptionHandling.Utilities.ErrorCode import ErrorCode
from ExceptionHandling.Model.Exceptions import ValidationError

import logging

class LeasingImportController:
    """
        Handles the Generic validation and returns the 
        respective vendors Object(Resman,Realpage)
    """

    def __validate(self,params:dict = None, date:str = None, servicerequest:ServiceRequest = None):
        """         
        Validates the input payload(communityUUId,customerUUId) 
        and returns the Boolean Value
        Parameters
        ----------
        params: Dictionary
        """       
        
        isvalid, _error = DataValidation.schema(Schema.PLATFORM_DATA,params) 
        
        if(_error):
            raise ValidationError(ErrorCode.ERROR_HTTP_0001, _error)

    def get_leases(self, servicerequest: ServiceRequest):
        """
        Returns the Leasing Endpoint results by resolving the Vendor using the factory design
        pattern and implement the respective third party endpoint.
    
        Parameters
        ----------
        servicerequest: Zato Request Object
        """
        self.__validate(params = servicerequest.payload, servicerequest = servicerequest)
        router = VendorRouter()
        outgoing_channel = router.resolve_vendor(servicerequest)
        logging.info("Outgoing Channel Response : {}".format(router))
        return outgoing_channel.get_leases(servicerequest)
        
