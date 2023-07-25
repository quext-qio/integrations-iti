import json

from zato.server.service import Service

from DataPushPullShared.Utilities.DataController import QuextIntegrationConstants
from DataPushPullShared.Utilities.RequestHelper import ApiSchema, build_params
from ExceptionHandling.Controller.ErrorHandlingController import ErrorHandlingController
from GuestCardShared.Controller.GuestCardController import GuestCardController
from Utils.AccessControl import AccessUtils
from VendorShared.Model.ServiceRequest import ServiceRequest
from VendorShared.Utilities.VendorConstants import VendorConstants
from Utils import CustomLogger

logging = CustomLogger.logger


class GuestCardService(Service):
    """
    @desc This is Guest card service which accepts the data to create guest card for a prospective resident.
    """

    class SimpleIO:
        """
        @desc This class handles the required and optional input fields required for GuestCard Controller Engine
        """
        # input_optional = ('relationshipid', 'phonenumber', 'email')    
        pass

    def handle_POST(self):
        """
        @desc This method handles the creation of prospects(guest card)
        """

        res = AccessUtils.check_access_control_v2(self.wsgi_environ, self.logger, self.response)
        if res:
            return

        payload = build_params(self.wsgi_environ, endpoint=ApiSchema.GUEST_CARD)

        service_request = ServiceRequest(self.cid, self.request, payload, self.cache, self.outgoing,
                                         VendorConstants.GUEST_CARD)
        controller_obj = GuestCardController()

        try:
            result = controller_obj.post_guestcards(service_request)
        except Exception as e:
            logging.error(e)
            ErrorHandlingController.build_error_response(self, e)
            self.logger.info("API Execution Failed")
        else:
            response = {QuextIntegrationConstants.DATA: result.dict(), QuextIntegrationConstants.ERROR: {}}
            self.response.payload = json.dumps(response, default=str)
            logging.info("API Final Response Success")
            self.response.status_code = QuextIntegrationConstants.HTTP_GOOD_RESPONSE_CODE
