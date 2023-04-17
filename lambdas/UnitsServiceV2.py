import json

from zato.server.service import Service

from DataPushPullShared.Utilities.DataController import QuextIntegrationConstants
from DataPushPullShared.Utilities.RequestHelper import ApiSchema, build_params
from ExceptionHandling.Controller.ErrorHandlingController import ErrorHandlingController
from UnitShared.Controller.UnitController import UnitController
from Utils.AccessControl import AccessUtils
from VendorShared.Model.ServiceRequest import ServiceRequest
from VendorShared.Utilities.VendorConstants import VendorConstants
from Utils import CustomLogger

logging = CustomLogger.logger

def lambda_function(self):
    
    params = build_params(self.wsgi_environ, endpoint=ApiSchema.UNIT_AVAILABILITY)
    service_request = ServiceRequest(cid=self.cid, request=self.request, payload=params, outgoing=self.outgoing,
                                     purpose=VendorConstants.UNITS)
    controller_obj = UnitController()

    try:
        res, err = controller_obj.get_unit_availability(service_request)
    except Exception as e:
        logging.error(e)
        ErrorHandlingController.build_error_response(self, e)
        logging.debug("API Execution Failed ")
    else:
        response = {
            QuextIntegrationConstants.DATA: []
        }
        for community in res:
            community_dict = community.dict()
            response[QuextIntegrationConstants.DATA].append(community_dict)
            response.update(err)
        self.response.payload = json.dumps(response, default=str)
        logging.debug("API Final Response : {}".format(res))
        self.response.status_code = QuextIntegrationConstants.HTTP_GOOD_RESPONSE_CODE
