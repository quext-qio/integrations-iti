import json
import logging
import re

from DataPushPullShared.Model.CommonStructure import CommonStructure, Community, Property, PhysicalLocation, \
    GpsLocation, Accounting, ContactMethods, CustomerEvent, LeaseTransaction, TransactionCode, Resident, Lease, \
    ResidentialSpace, FloorPlan, Event, Unit, Amenity
from DataPushPullShared.RentDynamics.RentDynamicsMapper import RentDynamicsConstants
from DataPushPullShared.Utilities.DataController import Datasource, QuextIntegrationConstants, ValidationConstants, \
    decrypt, AmenityConstants
from DataPushPullShared.Utilities.DatabaseConnection import getSSHConfigData, getConfigData, executeQuery
from DataPushPullShared.Utilities.HTTPHelper import HTTPRequest, sendRequest
from DataPushPullShared.Config.DatabaseConfig import database_key


class NewCoConstants:
    RESIDENT_TRANSACTION_URL = 'https://newco.maderaresidential.com/api/quext/payment'


class NewCoDatabaseMapper:
    @staticmethod
    def get_customer_events_RentDynamics(data: CommonStructure, dataSource: Datasource, params: dict = None):
        _config = getConfigData(dataSource)
        _ssh_config = getSSHConfigData(dataSource)
        db = []
        try:
            if params['end_date'] > params['start_date']:
                db = executeQuery(RentDynamicsConstants.GET_CUSTOMER_EVENTS, _config, _ssh_config, [params])
            else:
                responseObj = {QuextIntegrationConstants.DATA: {},
                               QuextIntegrationConstants.ERROR: {}}
                responseObj[QuextIntegrationConstants.ERROR][
                    QuextIntegrationConstants.MESSAGE] = 'End date must be greater than Start date'
                return {}, responseObj

        except:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'Data fetch error'
            return {}, responseObj

        if len(db) != 0:
            for item in db:
                if str(item['property_id']) not in data.data.community:
                    _community = Community("", "", str(item['property_id']),
                                           "", 0,
                                           Property('', [],
                                                    PhysicalLocation("", '', '',
                                                                     '', ''),
                                                    GpsLocation("", "")), [],
                                           ContactMethods('', '', '', ''), None, None, None, None, Accounting(), [], [])
                    data.data.community[str(item['property_id'])] = _community
                _customerEvent = CustomerEvent(str(item['event_type']), str(item['event_id']), str(item['event_date']),
                                               str(item["created_at"]),
                                               int(item["person_id"]))
                data.data.community[str(item['property_id'])].events.append(_customerEvent)
            return data, None
        elif len(db) == 0:
            return False, None            


    @staticmethod
    def get_transactions_RentDynamics(data: CommonStructure, dataSource: Datasource, params: dict = None):
        if not (params['end_date'] > params['start_date']):
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'End date must be greater than Start date'
            return {}, responseObj

        _parameter = {'residentId': params['resident_id'],
                      'start_date': params['start_date'],
                      'end_date': params['end_date']}

        res = sendRequest(HTTPRequest.GET, NewCoConstants.RESIDENT_TRANSACTION_URL, '', '', {}, _parameter)
        isValid, output = validateAPIResponseData(res.status_code)

        if not isValid:
            return False, output

        _community = Community("", "", 'Test', "", 0, Property('', [], PhysicalLocation("", '', '', '', ''),
                                                               GpsLocation("", "")), [],
                               ContactMethods('', '', '', ''), None, None, None, None, Accounting(), [])

        _transactions = json.loads(res.text)['result'][0]['transactions']
        paymentID = set()

        if len(_transactions) < 1:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'No Records Found'
            return {}, responseObj

        for item in _transactions:
            _date = str(item['due_at']).split(' ')[0]
            _description = item['charge_description']

            if item['is_credit']:
                _description = 'CREDIT#####' + _description

            _transaction = LeaseTransaction(item['transaction_id'], _date, _date, item['charge_id'],
                                            item['charge_description'], item['amount'], '', 'transaction',
                                            _description, item['is_paid'])

            _community.lease_transaction.append(_transaction)

            for payment in item['payments']:
                _id = payment['id']
                _payment_date = str(payment['created_at']).split(' ')[0]
                if _id not in paymentID:
                    paymentID.add(_id)
                    _payment_transaction = LeaseTransaction(_id, _payment_date, _payment_date, '',
                                                            payment['payment_type'], payment['amount'], '', 'payment',
                                                            payment['payment_type'])
                    _community.lease_transaction.append(_payment_transaction)

        data.data.community[str(123456)] = _community
        return data, None

    @staticmethod
    def get_transactions_RentDynamics_Test(data: CommonStructure, dataSource: Datasource, params: dict = None):
        _config = getConfigData(dataSource)
        _ssh_config = getSSHConfigData(dataSource)
        db = []
        try:
            if params['end_date'] > params['start_date']:
                db = executeQuery(RentDynamicsConstants.GET_TRANSACTIONS, _config, _ssh_config, [params])
            else:
                responseObj = {QuextIntegrationConstants.DATA: {},
                               QuextIntegrationConstants.ERROR: {}}
                responseObj[QuextIntegrationConstants.ERROR][
                    QuextIntegrationConstants.MESSAGE] = 'End date must be greater than Start date'
                return {}, responseObj
        except:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'Data fetch error'
            return {}, responseObj

        if len(db) != 0:
            for item in db:
                if str(item['community_id']) not in data.data.community:
                    _community = Community("", "", str(item['community_id']),
                                           "", 0,
                                           Property('', [],
                                                    PhysicalLocation("", '', '',
                                                                     '', ''),
                                                    GpsLocation("", "")), [],
                                           ContactMethods('', '', '', ''), None, None, None, None, Accounting(), [])
                    data.data.community[str(item['community_id'])] = _community

                _transaction = LeaseTransaction(item['transaction_id'], item['transaction_posted_date'], '',
                                                item['transaction_charge_code_id'],
                                                item['transaction_charge_code_name'],
                                                item['transaction_amount'], '', item['transaction_type'],
                                                item['transaction_notes'])
                data.data.community[str(item['community_id'])].lease_transaction.append(_transaction)
            return data, None
        else:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'No Records Found'
            return {}, responseObj

    @staticmethod
    def get_chargeCodes_RentDynamics(data: CommonStructure, dataSource: Datasource, params: dict = None):
        _config = getConfigData(dataSource)
        _ssh_config = getSSHConfigData(dataSource)
        db = []
        try:
            db = executeQuery(RentDynamicsConstants.GET_CHARGECODES, _config, _ssh_config, [params])
        except:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'Data fetch error'
            return {}, responseObj

        if len(db) != 0:
            for item in db:
                if str(item['community_id']) not in data.data.community:
                    _community = Community("", "", str(item['community_id']),
                                           "", 0,
                                           Property('', [],
                                                    PhysicalLocation("", '', '',
                                                                     '', ''),
                                                    GpsLocation("", "")), [],
                                           ContactMethods('', '', '', ''), None, None, None, None, Accounting())
                    data.data.community[str(item['community_id'])] = _community

                _transactionCode = TransactionCode(item['charge_code_id'], item['charge_code_name'])
                data.data.community[str(item['community_id'])].accounting.transaction_codes.append(_transactionCode)
            return data, None
        else:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'No Records Found'
            return {}, responseObj

    @staticmethod
    def get_properties_RentDynamics(data: CommonStructure, dataSource: Datasource, params: dict = None):
        _config = getConfigData(dataSource)
        _ssh_config = getSSHConfigData(dataSource)
        db = []
        try:
            db = executeQuery(RentDynamicsConstants.GET_PROPERTIES, _config, _ssh_config, [params])
        except:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'Data fetch error'
            return {}, responseObj

        if len(db) != 0:
            for item in db:
                if str(item['property_id']) not in data.data.community:
                    _community = Community(str(item['property_name']), "", str(item['property_id']),
                                           "", 0,
                                           Property('', [],
                                                    PhysicalLocation(str(item['address']), '', str(item['city']),
                                                                     str(item['state']), str(item['zip'])),
                                                    GpsLocation("", "")), [],
                                           ContactMethods(str(item['phone']), '', '', ''))
                    data.data.community[str(item['property_id'])] = _community
            return data, None
        else:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'No Records Found'
            return {}, responseObj

    @staticmethod
    def get_prospects_RentDynamics(data: CommonStructure, dataSource: Datasource, params: dict = None):
        _config = getConfigData(dataSource)
        _ssh_config = getSSHConfigData(dataSource)
        db = []
        try:
            db = executeQuery(RentDynamicsConstants.GET_PROSPECTS, _config, _ssh_config, [params])
        except:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'Data fetch error'
            return {}, responseObj

        if len(db) != 0:
            for item in db:
                if str(item['community_id']) not in data.data.community:
                    _community = Community('', "", str(item['community_id']),
                                           '', 0,
                                           Property('', [], PhysicalLocation('',
                                                                             '',
                                                                             '',
                                                                             '', ''),
                                                    GpsLocation('', '')), [],
                                           ContactMethods('', '', '', ''), None, [])
                    data.data.community[str(item['community_id'])] = _community
                _resident = Resident(str(item['first_name']), str(item['last_name']), '',
                                     '', str(item['email']), str(item['phone']),
                                     str(item['address']), str(item['city']), str(item['state']), str(item['postal']),
                                     str(item['move_in_date']), '', item['desired_bedrooms'],
                                     item['additional_occupants'], str(item['pets']), 0,
                                     item['prospect_id'], '',
                                     '',
                                     '', '', '')
                data.data.community[str(item['community_id'])].people.append(_resident)
            return data, None
        else:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'No Records Found'
            return {}, responseObj

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

    @staticmethod
    def get_residents_RentDynamics(data: CommonStructure, dataSource: Datasource, params: dict = None):
        _config = getConfigData(dataSource)
        _ssh_config = getSSHConfigData(dataSource)
        db = []
        try:
            if (params['move_out_date'] is not None and params['move_out_date'] > params['move_in_date']) or \
                    (len(params['move_out_date']) == 0):
                db = executeQuery(RentDynamicsConstants.GET_RESIDENTS, _config, _ssh_config, [params])
            else:
                responseObj = {QuextIntegrationConstants.DATA: {},
                               QuextIntegrationConstants.ERROR: {}}
                responseObj[QuextIntegrationConstants.ERROR][
                    QuextIntegrationConstants.MESSAGE] = 'move_out_date must be greater than move_in_date'
                return {}, responseObj
        except:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'Data fetch error'
            return {}, responseObj
        valid_Pattern = re.compile(ValidationConstants.SSN_REGEX)
        if len(db) != 0:
            for item in db:
                _ssn = None
                if item['ssn'] is None:
                    _ssn = None
                elif re.search('[a-zA-Z]', str(item['ssn'])) is not None:
                    _ssn = decrypt(str(item['ssn']), database_key['newco_key'])
                else:
                    temp_ssn = str(item['ssn']).strip().replace('-', '')
                    if valid_Pattern.match(temp_ssn) is not None:
                        _ssn = temp_ssn
                    else:
                        _ssn = None
                _lease = Lease(int(item['lease_id']), str(item['lease_start_date']), str(item['lease_expiration_date']),
                               item['is_active'], '', [])
                _resident = Resident(str(item['first_name']), str(item['last_name']), str(_ssn),
                                     str(item['date_of_birth']), str(item['email']), 
                                     str(str(item['phone']).strip().replace('-', '')).strip().replace(' ', ''),
                                     str(item['address']), str(item['city']), str(item['state']), str(item['postal']),
                                     '', '', 0, 0, '', int(item['resident_id']), item['prospect_id'],
                                     str(item['resident_type']),
                                     str(item['move_in_date']),
                                     '', '', str(item['move_out_date']))
                _lease.residents.append(_resident)
                data.data.community[str(item['community_id'])].units[
                    str(item['unit_id'])].lease = _lease
                data.data.community[str(item['community_id'])].units[
                    str(item['unit_id'])].name = str(item['unit_name'])
            return data, None
        else:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'No Records Found'
            return {}, responseObj

    @staticmethod
    def get_units_and_floorplans_RentDynamics(data: CommonStructure, dataSource: Datasource, params: dict = None):
        _config = getConfigData(dataSource)
        _ssh_config = getSSHConfigData(dataSource)
        db = []
        try:
            db = executeQuery(RentDynamicsConstants.UNITS_AND_FLOORPLANS, _config, _ssh_config, [params])
        except:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'Data fetch error'
            return {}, responseObj

        if len(db) != 0:
            for item in db:
                if str(item['community_id']) not in data.data.community:
                    _community = Community("", "", str(item['community_id']),
                                           '', 0,
                                           Property('', [], PhysicalLocation('',
                                                                             '',
                                                                             '',
                                                                             '', ''),
                                                    GpsLocation('', '')), [],
                                           ContactMethods('', '', '', ''))
                    data.data.community[str(item['community_id'])] = _community

                data.data.community[str(item['community_id'])].units[str(item['unit_id'])] = Unit(
                    str(item['unit_name']),
                    ResidentialSpace(int(item['bedroom_count']) if item['bedroom_count'] != None else 0,
                                     int(item['bathroom_count']) if item['bathroom_count'] != None else 0,
                                     0,
                                     str(item['unit_id']), [],
                                     int(item['square_feet']) if item['square_feet'] != None else 0, int(item['square_feet']) if item['square_feet'] != None else 0,
                                     '',
                                     FloorPlan('', str(item['unit_type_id']), '',
                                               '')),
                    [str(item['lease_status'])], '', 0,
                    float(item['market_rent_amount']) if item['market_rent_amount'] != None else 0,
                    float(item['rent_amount']) if item['rent_amount'] != None else 0, str(item['occupancy_status']), '', '', int(item['is_active']) if item['is_active'] != None else 0,
                    Event('', ''), Lease(0, '', '', 0, '', [], None, []), None, None)
            return data, None
        else:
            responseObj = {QuextIntegrationConstants.DATA: {},
                           QuextIntegrationConstants.ERROR: {}}
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.MESSAGE] = 'No Records Found'
            return {}, responseObj


def validateAPIResponseData(_responseCode):
    _error = {QuextIntegrationConstants.DATA: {},
              QuextIntegrationConstants.ERROR: {}}
    if _responseCode == 200:
        return True, _error
    elif _responseCode == 400:
        _error[QuextIntegrationConstants.ERROR]['error'] = 'Invalid Request'
        return False, _error
    else:
        _error[QuextIntegrationConstants.ERROR]['error'] = 'Invalid Request'
        return False, _error
