import enum

from DataPushPullShared.Utilities.DataController import QuextIntegrationConstants, DataController
from DataPushPullShared.MarketData.Interface.PlatformInterface import PlatformInterface
from DataPushPullShared.MarketData.Utilities.NewCoDatabaseMapper import NewCoDatabaseMapper
from DataPushPullShared.Utilities.QuextOperation import QuextOperation
from DataPushPullShared.MarketData.Utilities.UnitAvailabilityMapper import UnitAvailabilityMapper


class NewCoPlatform(PlatformInterface):
    def getRequestData(self, data,  platformData: dict, dataSource: enum = None):
        operation_details = getOperationDetails()
        data_controller = DataController()

        # Construct parameter to fetch Unit Availability
        communityID = {'community_id': int(platformData['communityID'])}

        error = None
        if operation_details[QuextIntegrationConstants.INPUT] is not None:
            data, error = data_controller.getData(data,
                                                  operation_details[QuextIntegrationConstants.INPUT],
                                                  dataSource, communityID)
        return data, error

    def formatResponse(self, data, error):
        operation_details = getOperationDetails()
        data_controller = DataController()
        if operation_details[QuextIntegrationConstants.OPERATION] is not None and error is None:
            data, error = data_controller.executeOperation(data,
                                                           operation_details[
                                                               QuextIntegrationConstants.OPERATION])
        response = {}
        if operation_details[QuextIntegrationConstants.OUTPUT] is not None and error is None:
            response = data_controller.getResponseData(data,
                                                       operation_details[QuextIntegrationConstants.OUTPUT])
            return response, error
        return data, error


def getOperationDetails():
    return {
        QuextIntegrationConstants.INPUT: [NewCoDatabaseMapper.getUnitDetails_UnitAvailability,
                                          NewCoDatabaseMapper.getAmenityDetailsFromCommunity],
        QuextIntegrationConstants.OPERATION: [QuextOperation.getUnitPrice],
        QuextIntegrationConstants.OUTPUT: UnitAvailabilityMapper.setUnitDetails
    }