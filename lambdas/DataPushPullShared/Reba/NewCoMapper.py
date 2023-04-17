import re

from DataPushPullShared.Model.CommonStructure import CommonStructure, Community, PhysicalLocation, GpsLocation, \
    Property, \
    Unit, Amenity, ResidentialSpace, ContactMethods
from DataPushPullShared.Utilities.DataController import Datasource, CommunityConstants, UnitConstants, AmenityConstants
from DataPushPullShared.Utilities.DatabaseConnection import getConfigData, getSSHConfigData, executeQuery


class NewCoMapper:
    @staticmethod
    def getUnitDetails_Reba(data: CommonStructure, dataSource: Datasource, params: dict = None):
        _config = getConfigData(dataSource)
        _ssh_config = getSSHConfigData(dataSource)

        param_type, parameter = NewCoMapper.getUnitsParamsType(params)
        if param_type is not None:
            db = executeQuery(param_type, _config, _ssh_config, parameter)

            if len(db) != 0:
                for item in db:
                    if str(item['community_id']) not in data.data.community.keys():
                        _community = Community(str(item['community_name']), "", str(item['community_id']),
                                               str(item['availability_status']), 0,
                                               Property('', [],
                                                        PhysicalLocation('', '', '', '', ''),
                                                        GpsLocation("", "")), [],
                                               ContactMethods('', '', '', ''))
                        data.data.community[str(item['community_id'])] = _community

                    _unit = Unit(str(item['unit_name']),
                                 ResidentialSpace(int(item['bedroom_count']),
                                                  int(item['bathroom_count']),
                                                  int(item['half_bath_count']),
                                                  str(item['unit_id']), [],
                                                  int(item['square_feet']), int(item['square_feet']),
                                                  str(item['floor'])), [], '', 0, 0, 0, '', '', '', 0)
                    data.data.community[str(item['community_id'])].units[str(item['unit_id'])] = _unit

                return data, None
            else:
                error_message = {'error_code': 200, 'message': {'response': 'No Records Found'}}
                return None, error_message
        else:
            error_message = {'error_code': 400, 'message': {'parameter': 'Invalid Parameter'}}
            return None, error_message

    @staticmethod
    def getUnitsParamsType(params: dict = None):
        if params is not None:
            if 'unit_id' in params:
                if isinstance(params['unit_id'], list):
                    param_dict = []
                    for item in params['unit_id']:
                        param_dict.append({'unit_id': item})
                    return UnitConstants.UNIT_ID, param_dict
                else:
                    return UnitConstants.UNIT_ID, [{'unit_id': params['unit_id']}]
            elif 'community_id' in params:
                if isinstance(params['community_id'], list):
                    param_dict = []
                    for item in params['community_id']:
                        param_dict.append({'community_id': item})
                    return UnitConstants.UNIT_COMMUNITY_ID, param_dict
                else:
                    return UnitConstants.UNIT_COMMUNITY_ID, [{'community_id': params['community_id']}]
            else:
                return None, None
        else:
            return UnitConstants.UNIT, None

    @staticmethod
    def getAmenityDetails_Reba(data: CommonStructure, dataSource: Datasource, params: dict = None):
        _config = getConfigData(dataSource)
        _ssh_config = getSSHConfigData(dataSource)

        param_type, parameter = NewCoMapper.getAmenityParamsType(params)
        if param_type is not None:
            db = executeQuery(param_type, _config, _ssh_config, parameter)

            if len(db) != 0:
                for item in db:
                    if str(item['community_id']) not in data.data.community.keys():
                        _community = Community(str(item['community_name']), "", str(item['community_id']), "", 0,
                                               Property('', [], PhysicalLocation('', '', '', '', ''),
                                                        GpsLocation('', ''))
                                               , [], ContactMethods('', '', '', ''))
                        data.data.community[str(item['community_id'])] = _community

                    if str(item['unit_name']) not in data.data.community[str(item['community_id'])].units.keys():
                        _unit = Unit(str(item['unit_name']),
                                     ResidentialSpace(0, 0, 0, str(item['unit_id']), [], 0, 0, ''), [], '', 0.0, 0.0,
                                     0.0, '', '', '', 0)
                        data.data.community[str(item['community_id'])].units[str(item['unit_id'])] = _unit

                    _amenity = Amenity(str(item['amenity_name']), '', str(item['amenity_value']), '', '')
                    data.data.community[str(item['community_id'])].units[
                        str(item['unit_id'])].unit_amenities.append(_amenity)
                return data, None
            else:
                error_message = {'error_code': 200, 'message': {'response': 'No Records Found'}}
                return None, error_message
        else:
            error_message = {'error_code': 400, 'message': {'parameter': 'Invalid Parameter'}}
            return None, error_message

    @staticmethod
    def getAmenityParamsType(params: dict = None):
        if params is not None:
            if 'unit_id' in params:
                if isinstance(params['unit_id'], list):
                    param_dict = []
                    for item in params['unit_id']:
                        param_dict.append({'unit_id': item})
                    return AmenityConstants.AMENITY_UNIT_ID, param_dict
                elif isinstance(params['unit_id'], str):
                    return AmenityConstants.AMENITY_UNIT_ID, [{'unit_id': params['unit_id']}]
                elif isinstance(params['unit_id'], int):
                    return AmenityConstants.AMENITY_UNIT_ID, [{'unit_id': params['unit_id']}]
                else:
                    return None, None
            elif 'community_id' in params:
                if isinstance(params['community_id'], list):
                    param_dict = []
                    for item in params['community_id']:
                        param_dict.append({'community_id': item})
                    return AmenityConstants.AMENITY_COMMUNITY_ID, param_dict
                elif isinstance(params['community_id'], str):
                    return AmenityConstants.AMENITY_COMMUNITY_ID, [{'community_id': params['community_id']}]
                elif isinstance(params['community_id'], int):
                    return AmenityConstants.AMENITY_COMMUNITY_ID, [{'community_id': params['community_id']}]
                else:
                    return None, None
            else:
                return None, None
        else:
            return None, None

    @staticmethod
    def getCommunityDetails_Reba(data: CommonStructure, dataSource: Datasource, params: dict = None):
        _config = getConfigData(dataSource)
        _ssh_config = getSSHConfigData(dataSource)

        param_type, parameter = NewCoMapper.getCommunityParamsType(params)
        if param_type is not None:
            db = executeQuery(param_type, _config, _ssh_config, parameter)
            if len(db) != 0:
                for item in db:
                    _community = Community(str(item['community_name']), "", str(item['community_id']),
                                           str(item['availability_status']), 0,
                                           Property('', [],
                                                    PhysicalLocation(str(item['address']),
                                                                     str(item['address2']),
                                                                     str(item['city']),
                                                                     str(item['state']),
                                                                     str(item['zip'])), GpsLocation("", "")), [],
                                           ContactMethods('', '', '', ''))
                    data.data.community[str(item['community_id'])] = _community
                return data, None
            else:
                error_message = {'error_code': 200, 'message': {'response': 'No Records Found'}}
                return None, error_message
        else:
            error_message = {'error_code': 400, 'message': {'parameter': 'Invalid Parameter'}}
            return None, error_message

    @staticmethod
    def getCommunityParamsType(params: dict = None):
        if params is not None:
            if 'status' in params and params['status'] == 'current':
                return CommunityConstants.COMMUNITY_AFTER_DEPOSITION, None
            elif 'status' in params and params['status'] == 'former':
                return CommunityConstants.COMMUNITY_BEFORE_DEPOSITION, None
            elif 'customer_id' in params:
                return CommunityConstants.COMMUNITY_CUSTOMER_ID, params['customer_id']
            elif 'community_id' in params:
                if isinstance(params['community_id'], list):
                    param_dict = []
                    for item in params['community_id']:
                        param_dict.append({'community_id': item})
                    return CommunityConstants.COMMUNITY_ID, param_dict
                elif isinstance(params['community_id'], str):
                    return CommunityConstants.COMMUNITY_ID, [{'community_id': params['community_id']}]
                elif isinstance(params['community_id'], int):
                    return CommunityConstants.COMMUNITY_ID, [{'community_id': params['community_id']}]
                else:
                    return None, None
            else:
                return None, None
        else:
            return CommunityConstants.COMMUNITY, None
