import json
from decimal import Decimal
from contextlib import closing
from controller.query_controller import QueryController


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError

class NewCoMapper:
    global db_object 
    db_object = QueryController() 

    @staticmethod
    def get_chargeCodes_RentDynamics(params: dict):
        # _config = getConfigData(dataSource)
        # _ssh_config = getSSHConfigData(dataSource)
        # db = []
        # try:
        #     db = executeQuery(RentDynamicsConstants.GET_CHARGECODES, _config, _ssh_config, [params])
        # except:
        #     responseObj = {QuextIntegrationConstants.DATA: {},
        #                    QuextIntegrationConstants.ERROR: {}}
        #     responseObj[QuextIntegrationConstants.ERROR][
        #         QuextIntegrationConstants.MESSAGE] = 'Data fetch error'
        #     return {}, responseObj

        try:
            with closing(db_object.get_db_session()) as session:
                cursor = session.cursor(dictionary=True)
                path = "newco_queries/get_charge_codes.sql"
                output = db_object.read_query(path, "rent_dynamics", "charge_codes", 0.0)
                cursor.execute(output, params)
                
                # Fetch all rows
                result = cursor.fetchall()
                for item in result:
                    decimal_value = item['amount']
                    item['amount'] = float(decimal_value)
                
                # TODO: Map the data to the expected format

                return True, result
        
        except Exception as e:
            print(f"An error occurred while retrieving data from the database: {str(e)}")
            return False, [{"error":f"An error occurred while retrieving data from the database: {str(e)}"}]

        # if len(db) != 0:
        #     for item in db:
        #         if str(item['community_id']) not in data.data.community:
        #             _community = Community("", "", str(item['community_id']),
        #                                    "", 0,
        #                                    Property('', [],
        #                                             PhysicalLocation("", '', '',
        #                                                              '', ''),
        #                                             GpsLocation("", "")), [],
        #                                    ContactMethods('', '', '', ''), None, None, None, None, Accounting())
        #             data.data.community[str(item['community_id'])] = _community

        #         _transactionCode = TransactionCode(item['charge_code_id'], item['charge_code_name'])
        #         data.data.community[str(item['community_id'])].accounting.transaction_codes.append(_transactionCode)
        #     return data, None
        # else:
        #     responseObj = {QuextIntegrationConstants.DATA: {},
        #                    QuextIntegrationConstants.ERROR: {}}
        #     responseObj[QuextIntegrationConstants.ERROR][
        #         QuextIntegrationConstants.MESSAGE] = 'No Records Found'
        #     return {}, responseObj