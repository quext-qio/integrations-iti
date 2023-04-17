from DataPushPullShared.Model.CommonStructure import CommonStructure, Community, Property, PhysicalLocation, \
    GpsLocation, ContactMethods, ResidentialSpace, FloorPlan, Event, Amenity, Unit
from DataPushPullShared.Utilities.DataController import Datasource, QuextIntegrationConstants, convertCountryToAplha3, \
    validateStateField, validatePostalCode, AmenityConstants
from DataPushPullShared.Utilities.DatabaseConnection import getConfigData, getSSHConfigData, executeQuery
from DataPushPullShared.MarketData.Utilities.UnitAvailabilityMapper import UnitAvailabilityUnitConstants


class NewCoDatabaseMapper:
    @staticmethod
    def getUnitDetails_UnitAvailability(data: CommonStructure, dataSource: Datasource, params: dict = None):
        _config = getConfigData(dataSource)
        _ssh_config = getSSHConfigData(dataSource)
        db = []
        try:
            db = executeQuery(UnitAvailabilityUnitConstants.UNIT_BY_COMMUNITY_ID, _config, _ssh_config, [params])
        except:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'Data fetch error'
            return {}, responseObj

        if len(db) != 0:
            for item in db:
                if str(item['community_id']) not in data.data.community:
                    _country = convertCountryToAplha3('')
                    _state = validateStateField(str(item['state']))
                    _zip = validatePostalCode(str(item['zip']))
                    _community = Community(str(item['community_name']), "", str(item['community_id']),
                                           '', 0,
                                           Property(_country, [], PhysicalLocation(str(item['address']),
                                                                                   str(item['address2']),
                                                                                   str(item['city']),
                                                                                   _state, _zip),
                                                    GpsLocation('', '')), [],
                                           ContactMethods('', '', '', ''))
                    data.data.community[str(item['community_id'])] = _community
                data.data.community[str(item['community_id'])].units[str(item['unit_id'])] = Unit(
                    str(item['unit_name']),
                    ResidentialSpace(int(item['bedroom_count']),
                                     int(item['bathroom_count']),
                                     int(item['half_bath_count']),
                                     str(item['unit_id']), [],
                                     int(item['square_feet']),
                                     int(item['square_feet']),
                                     str(item['floor']),
                                     FloorPlan(str(item['unit_type']), '', str(item['image_url']),
                                               str(item['virtual_tour_url']))),
                    [str(item['unit_status'])], '', 0,
                    float(item['market_rent_amount']),
                    float(item['rent_amount']), '', str(item['valid_starting']), str(item['available_date']), 0,
                    Event('', str(item['vacate_date'])), None, None, None)
        return data, None

    @staticmethod
    def getAmenityDetailsFromCommunity(data: CommonStructure, dataSource: Datasource, params: dict = None):
        _config = getConfigData(dataSource)
        _ssh_config = getSSHConfigData(dataSource)
        db = executeQuery(AmenityConstants.AMENITY_COMMUNITY_ID, _config, _ssh_config, [params])
        if len(db) != 0:
            for item in db:
                _amenity = Amenity(str(item['amenity_name']), '', str(item['amenity_value']), '', '')
                data.data.community[str(item['community_id'])].units[
                    str(item['unit_id'])].unit_amenities.append(
                    Amenity(str(item['amenity_name']), '', str(item['amenity_value']), '', ''))

        return data, None
