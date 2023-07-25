import enum
import json
import dateutil.parser

from rentdynamics.client import Client
from DataPushPullShared.MarketData.Config.Config import rent_dynamic_config
from DataPushPullShared.Utilities.Convert import Convert
from DataPushPullShared.Utilities.DataController import QuextIntegrationConstants, DataController
from DataPushPullShared.MarketData.Interface.PlatformInterface import PlatformInterface
from DataPushPullShared.MarketData.Utilities.UnitAvailabilityMapper import UnitAvailabilityUnitConstants, UnitAvailabilityMapper
from DataPushPullShared.Model.CommonStructure import CommonStructure, Community, PhysicalLocation, GpsLocation, Property, \
    Unit, ResidentialSpace, ContactMethods, FloorPlan, Event


class RentDynamicsPlatform(PlatformInterface):
    def getRequestData(self, data: CommonStructure, platformData: dict, dataSource: enum = None):
        api_key = rent_dynamic_config['api_key']
        api_secret = rent_dynamic_config['api_secret_key']
        communityID = platformData['CommunityID']
        development = rent_dynamic_config['development']
        if development == 'False':
            development = False
        else:
            development = True
        url = UnitAvailabilityUnitConstants.RENT_DYNAMICS_URL.replace("communityID", str(communityID))
        client = Client(api_key=api_key, api_secret=api_secret, development=development)
        response = client.get(url)
        result = json.loads(response.text)
        if response.status_code == 200:
            if str(communityID) not in data.data.community:
                _community = Community(result['communityInformation']['communityName'], "", str(communityID),
                                       '', 0,
                                       Property('', [], PhysicalLocation(result['communityInformation']['communityAddress']['addressLine1'],
                                                                         result['communityInformation']['communityAddress']['addressLine2'],
                                                                         result['communityInformation']['communityAddress']['city'],
                                                                         result['communityInformation']['communityAddress']['state'],
                                                                         result['communityInformation']['communityAddress']['zip']),
                                                GpsLocation('', '')), [],
                                       ContactMethods(result['communityInformation']['communityPhoneNumber'], '', '',
                                                      result['communityInformation']['communityEmail']))
                data.data.community[str(communityID)] = _community

            for keyFloorPlan in result['floorplans']:
                for keyUnit in keyFloorPlan['floorplan']['units']:
                    if keyUnit['availableDate']:
                        available_date = dateutil.parser.parse((keyUnit['availableDate']))
                        availableDate = available_date.strftime('%d-%m-%Y')
                    else:
                        availableDate = None
                    data.data.community[str(communityID)].units[str(keyUnit['unitID'])] = Unit(
                        str(keyUnit['unitNumber']),
                        ResidentialSpace(Convert.toInt(keyUnit['bed']),
                                         Convert.toInt(keyUnit['bath']),
                                         0,
                                         str(keyUnit['unitID']), [],
                                         Convert.toInt(keyUnit['sqft']['minSqft']), Convert.toInt(keyUnit['sqft']['maxSqft']),
                                         '',
                                         FloorPlan(str(keyUnit['unitName']), '',
                                                   str(keyFloorPlan['floorplan']['floorPlanImageUrl']),
                                                   "")),
                        [''], str(keyUnit['isUnitAvailable']),
                        Convert.toFloat(keyFloorPlan['floorplan']['pricingData']['effectiveRent']['min']),
                        Convert.toFloat(keyUnit['pricing']['marketRate']),
                        Convert.toFloat(keyUnit['pricing']['effectiveRent']['effectiveRentMax']), '', '', str(availableDate), 0,
                        Event('', ''), None, None, None)
            return data, None
        else:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = result['errorMessage']
            return {}, responseObj

    def formatResponse(self, data, error):
        data_controller = DataController()
        response = {}
        if error is None:
            response = data_controller.getResponseData(data,
                                                       UnitAvailabilityMapper.setUnitDetails)
            return response, error
        return data, error

