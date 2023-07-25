import json
import logging
import datetime
import re

from DataPushPullShared.Model.CommonStructure import CommonStructure


class RentDynamicsConstants:
    UNITS_AND_FLOORPLANS = 'get_all_units'
    GET_RESIDENTS = 'get_residents'
    GET_PROSPECTS = 'get_prospects'
    GET_PROPERTIES = 'get_properties'
    GET_CHARGECODES = 'get_charge_codes'
    GET_TRANSACTIONS = 'get_all_transactions'
    GET_CUSTOMER_EVENTS = 'get_customer_events'
    Description_constants = ['Renter\'s', "Rent", "Utility", "Trash", "Pest"]
    TextNumberRegex = "([a-zA-Z]+)([0-9]+)"


class RentDynamicsMapper:
    @staticmethod
    def setCustomerEventDetails(data: CommonStructure):
        result = []
        communityData = data.data.community
        for keyCommunity in communityData.keys():
            for item in communityData[keyCommunity].events:
                temp = re.compile(RentDynamicsConstants.TextNumberRegex)
                event_id = (temp.match(item.id).groups())[1]
                event_record = {
                    "eventType": item.type,
                    "eventDate": item.date,
                    "internalPMSystemID": event_id,
                    "agentID": "",
                    "adSource": "",
                    "created": item.created_at,
                    "eventDetails": '',
                    "personID": item.person_id
                }
                result.append(event_record)
        return result

    @staticmethod
    def setPropertyDetails(data: CommonStructure):
        result = []
        communityData = data.data.community
        for item in communityData.keys():
            # here we have to replace 'communityUUID' string with actual community UUID
            _data = {'propertyId': communityData[item].quext_id,
                     'name': communityData[item].short_name,
                     'address': communityData[item].property.physical_location.address,
                     'city': communityData[item].property.physical_location.city,
                     'state': communityData[item].property.physical_location.state,
                     'zip': communityData[item].property.physical_location.postal_code,
                     'phoneNumber': communityData[item].contact_methods.phone}
            result.append(_data)
        return result

    @staticmethod
    def setUnitDetails(data: CommonStructure):
        result = []
        communityData = data.data.community
        unit_dict = {}
        for keyCommunity in communityData.keys():
            for keyUnit in communityData[keyCommunity].units.keys():
                _unit = data.data.community[keyCommunity].units[keyUnit]

                if _unit.residential_space.floor_plan.floor_plan_id not in unit_dict.keys():
                    _desc = str(_unit.residential_space.bedrooms) + " Bed, " + \
                            str(float(_unit.residential_space.full_bathrooms)) + " Bath"
                    unit_dict[_unit.residential_space.floor_plan.floor_plan_id] = {
                        'floorPlanId': _unit.residential_space.floor_plan.floor_plan_id,
                        'description': _desc,
                        'averageSquareFeet': (_unit.residential_space.min_sqft + _unit.residential_space.max_sqft) // 2,
                        'bedrooms': _unit.residential_space.bedrooms,
                        'bathrooms': float(_unit.residential_space.full_bathrooms),
                        'marketRent': _unit.price,
                        'unitCount': 0,
                        'units': [],
                        'unitsAvailable': 0,
                        'isFloorPlanActive': True
                    }
                else:
                    if unit_dict[_unit.residential_space.floor_plan.floor_plan_id]['marketRent'] > _unit.price:
                        unit_dict[_unit.residential_space.floor_plan.floor_plan_id]['marketRent'] = _unit.price
                unit_details = {'unitId': keyUnit, 'marketRent': _unit.price, 'occupancyStatus': _unit.occupancy_status,
                                'leaseStatus': _unit.status[0],
                                'unitNumber': _unit.name, 'isActive': True, 'exclude': False,
                                'rentReady': False}
                if ('Vacant - Not Leased' == _unit.status[0]) or ('NTV - Available' == _unit.status[0]):
                    unit_dict[_unit.residential_space.floor_plan.floor_plan_id]['unitsAvailable'] += 1
                unit_dict[_unit.residential_space.floor_plan.floor_plan_id]['unitCount'] += 1
                if _unit.leasable == 0:
                    unit_details['exclude'] = True
                    unit_details['isActive'] = False
                if _unit.status[0] == 'On Notice' or _unit.status[0] == 'Available':
                    unit_details['rentReady'] = True
                unit_dict[_unit.residential_space.floor_plan.floor_plan_id]['units'].append(unit_details)
                if unit_dict[_unit.residential_space.floor_plan.floor_plan_id]['unitCount'] == 0:
                    unit_dict[_unit.residential_space.floor_plan.floor_plan_id]['isFloorPlanActive'] = False

            _community = list(unit_dict.values())
            result.append(_community)
        return result[0]

    @staticmethod
    def setResidentDetails(data: CommonStructure):
        result = []
        resident_dict = {}
        communityData = data.data.community
        for keyCommunity in communityData.keys():
            for keyUnit in communityData[keyCommunity].units.keys():
                _unit = data.data.community[keyCommunity].units[keyUnit]
                for _resident in _unit.lease.residents:
                    if _resident.resident_id not in resident_dict.keys():
                        resident_dict[_resident.resident_id] = {
                            'residentId': _resident.resident_id,
                            'prospectId': _resident.prospect_id,
                            'firstName': _resident.first_name,
                            'lastName': _resident.last_name,
                            'SSN': _resident.ssn,
                            'DOB': _resident.date_of_birth,
                            'emailAddress': _resident.email,
                            'phone': _resident.phone,
                            'address': communityData[keyCommunity].property.physical_location.address,
                            'apt': _unit.name,
                            'unitId': keyUnit,
                            'city': communityData[keyCommunity].property.physical_location.city,
                            'state': communityData[keyCommunity].property.physical_location.state,
                            'zip': communityData[keyCommunity].property.physical_location.postal_code,
                            'leaseStartDate': _unit.lease.lease_start_date,
                            'leaseEndDate': _unit.lease.lease_end_date,
                            'leaseNumber': _unit.lease.lease_id,
                            'moveInDate': _resident.actual_move_in_date,
                            'moveOutDate': _resident.actual_move_out_date,
                            'customerInfo': _resident.resident_type,
                            'isLeasee': True
                        }
            result.append(list(resident_dict.values()))
        return result[0]

    @staticmethod
    def setProspectDetails(data: CommonStructure):
        result = []
        resident_dict = {}
        communityData = data.data.community
        for keyCommunity in communityData.keys():

            for _person in data.data.community[keyCommunity].people:

                if _person.prospect_id not in resident_dict.keys():
                    resident_dict[_person.prospect_id] = {
                        'prospectId': _person.prospect_id,
                        'firstName': _person.first_name,
                        'middleName': "",
                        'lastName': _person.last_name,
                        'emailAddress': _person.email,
                        'phone': _person.phone,
                        'address': _person.address,
                        'city': _person.city,
                        'state': _person.state,
                        'zip': _person.postal,
                        'targetMoveInDate': _person.desired_move_in_date,
                        'desiredBedrooms': _person.desired_bed_rooms,
                        'desiredNumberOccupants': _person.additional_occupants,
                        'petInfo': _person.pets
                    }
            result.append(list(resident_dict.values()))
        return result[0]

    @staticmethod
    def setChargeCode(data: CommonStructure):
        result = []
        communityData = data.data.community

        for keyCommunity in communityData.keys():

            for charge in communityData[keyCommunity].accounting.transaction_codes:
                result.append({
                    "description": charge.charge_code_name,
                    "chargeCode": charge.charge_code_id
                })
        return result

    @staticmethod
    def setTransaction(data: CommonStructure):
        result = []
        communityData = data.data.community

        for keyCommunity in communityData.keys():

            for item in communityData[keyCommunity].lease_transaction:
                transactionType = item.transaction_type.lower()
                transactionAmount = str(item.transaction_amount)
                is_credit = True if item.transaction_notes.split('#####')[0] == 'CREDIT' else False

                if is_credit:
                    item.transaction_notes = ''.join(item.transaction_notes.split('#####')[1:])

                if transactionType == "transaction":
                    transactionType = 'Charge'
                elif transactionType == "payment":
                    transactionType = 'Payment'
                    item.transaction_notes = 'Payment: ' + item.transaction_notes

                if is_credit:
                    transactionAmount = '-' + str(transactionAmount)

                transaction_record = {
                    "uniqueIdentifier": item.transaction_id,
                    "transactionDate": item.transaction_posted_date,
                    "amount": transactionAmount,
                    "transactionType": transactionType,
                    "chargeCode": item.transaction_charge_code_id,
                    "note": item.transaction_notes,
                    "description": '',
                    "isPaid": item.transaction_isPaid if (transactionType != "payment") or is_credit else None
                }
                _date = item.transaction_posted_date.split('-')
                trans_date = datetime.date(int(_date[0]), int(_date[1]), int(_date[2]))
                expire_date = trans_date + datetime.timedelta(days=30)
                transaction_record['description'] = item.transaction_charge_code_name + " for " + str(
                    trans_date) + ' to ' + str(expire_date)

                result.append(transaction_record)

        return result
