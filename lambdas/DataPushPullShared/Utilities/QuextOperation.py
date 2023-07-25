from DataPushPullShared.Model.CommonStructure import CommonStructure
from DataPushPullShared.Utilities.DataController import Datasource, CommunityConstants
from DataPushPullShared.Utilities.DatabaseConnection import getConfigData, getSSHConfigData, executeQuery


class QuextOperation:
    @staticmethod
    def calculateUnitStatus(data, params: [object]):
        return data

    @staticmethod
    def setCommunityName(data: CommonStructure):
        _config = getConfigData(Datasource.NEWCO)
        _ssh_config = getSSHConfigData(Datasource.NEWCO)

        params = []
        for _id in data.data.community.keys():
            params.append({'community_id': _id})
        db = executeQuery(CommunityConstants.COMMUNITY_OPERATION_ID, _config, _ssh_config, params)
        if len(db) != 0:
            for item in db:
                data.data.community[item['community_id']].amenity_id = item['community_name']
            return data, None
        else:
            error_message = {'error_code': 200, 'message': {'response': 'No Records Found'}}
            return None, error_message

    @staticmethod
    def getUnitPrice(data: CommonStructure):
        communityData = data.data.community
        for keyCommunity in communityData.keys():
            for keyUnit in communityData[keyCommunity].units.keys():
                price = communityData[keyCommunity].units[keyUnit].market_rent
                for item in communityData[keyCommunity].units[keyUnit].unit_amenities:
                    price += float(item.added_rent_value)
                communityData[keyCommunity].units[keyUnit].price = price
        return data, None