import datetime
import logging

from DataPushPullShared.Model.CommonStructure import CommonStructure


class UnitAvailabilityUnitConstants:
    UNIT_BY_COMMUNITY_ID = 'units_by_community_unitavailability'
    RENT_DYNAMICS_URL = '/communities/communityID/floorplanAvailableUnits'


MonthDict = {"JAN": 1,
             "FEB": 2,
             "MAR": 3,
             "APR": 4,
             "MAY": 5,
             "JUN": 6,
             "JUL": 7,
             "AUG": 8,
             "SEP": 9,
             "OCT": 10,
             "NOV": 11,
             "DEC": 12
             }


class UnitStatus:
    VACANT_NOT_LEASE = 'Vacant - Not Leased'
    NTV_AVAILABLE = 'NTV - Available'
    REHAB = 'Rehab'
    RENTED = 'Rented'
    VACANT_LEASE = 'Vacant - Leased'
    PENDING_APPROVAL = 'Pending Approval'


class UnitAvailabilityMapper:

    @staticmethod
    def setUnitDetails(data: CommonStructure):
        result = {'property': {}, 'availability': [], 'vacant_units': {}}
        price_dict = {}
        communityData = data.data.community
        for keyCommunity in communityData.keys():
            _community = result
            _community['property']['name'] = data.data.community[keyCommunity].short_name
            _community['property']['address'] = data.data.community[keyCommunity].property.physical_location.address
            _community['property']['address2'] = data.data.community[keyCommunity].property.physical_location.address2
            _community['property']['city'] = data.data.community[keyCommunity].property.physical_location.city
            _community['property']['state'] = data.data.community[keyCommunity].property.physical_location.state
            _community['property']['postal'] = data.data.community[keyCommunity].property.physical_location.postal_code
            _community['property']['email'] = data.data.community[keyCommunity].contact_methods.email
            _community['property']['phone'] = data.data.community[keyCommunity].contact_methods.phone
            _community['property']['speed_dail'] = data.data.community[keyCommunity].contact_methods.speed_dial
            _community['property']['fax'] = data.data.community[keyCommunity].contact_methods.fax
            unit_count = 0
            for keyUnit in communityData[keyCommunity].units.keys():
                _unit = data.data.community[keyCommunity].units[keyUnit]
                unit_count += 1
                _status = _unit.status[0]

                available_date, expire_date = None, None,
                if _unit.available_date != 'None':
                    _date = _unit.available_date.split('-')
                    if len(_date) > 1 and _date[1].isalpha():
                        _date[1] = MonthDict.get(_date[1].upper())
                    available_date = datetime.date(int(_date[2]), int(_date[1]), int(_date[0]))
                    expire_date = datetime.date.today() + datetime.timedelta(days=30)

                if _unit.residential_space.floor_plan.name not in price_dict.keys():

                    price_dict[_unit.residential_space.floor_plan.name] = {
                        'name': _unit.residential_space.floor_plan.name,
                        'sqft_min': _unit.residential_space.min_sqft,
                        'sqft_max': _unit.residential_space.max_sqft,
                        'beds': _unit.residential_space.bedrooms,
                        'baths': _unit.residential_space.full_bathrooms,
                        'price': 0,
                        'availability': 0,
                        'image': _unit.residential_space.floor_plan.floor_plan_image,
                        'virtual_tour_url':
                            _unit.residential_space.floor_plan.virtual_tour_url}
                    if (_status == UnitStatus.VACANT_NOT_LEASE) or (_status == UnitStatus.NTV_AVAILABLE) or (
                            _status == UnitStatus.REHAB) or (_unit.availability == 'True'):
                        if available_date and expire_date:
                            if available_date <= expire_date:
                                price_dict[_unit.residential_space.floor_plan.name]['availability'] += 1

                                if price_dict[_unit.residential_space.floor_plan.name]['price'] == 0:
                                    price_dict[_unit.residential_space.floor_plan.name]['price'] = _unit.price
                                elif price_dict[_unit.residential_space.floor_plan.name]['price'] > _unit.price:
                                    price_dict[_unit.residential_space.floor_plan.name]['price'] = _unit.price

                                _community['vacant_units'][unit_count] = {'name': _unit.name,
                                                                          'square_feet': _unit.residential_space.min_sqft,
                                                                          'floor': _unit.residential_space.level_of_primary_entry,
                                                                          'bedrooms': _unit.residential_space.bedrooms,
                                                                          'bathrooms': _unit.residential_space.full_bathrooms,
                                                                          'rent_amount': _unit.rent_amount,
                                                                          'market_rent_amount': _unit.market_rent,
                                                                          'vacate_date': _unit.event.vacate_date,
                                                                          'type': _unit.residential_space.floor_plan.name}
                        else:
                            price_dict[_unit.residential_space.floor_plan.name]['availability'] += 1

                            if price_dict[_unit.residential_space.floor_plan.name]['price'] == 0:
                                price_dict[_unit.residential_space.floor_plan.name]['price'] = _unit.price
                            elif price_dict[_unit.residential_space.floor_plan.name]['price'] > _unit.price:
                                price_dict[_unit.residential_space.floor_plan.name]['price'] = _unit.price

                            _community['vacant_units'][unit_count] = {'name': _unit.name,
                                                                      'square_feet': _unit.residential_space.min_sqft,
                                                                      'floor': _unit.residential_space.level_of_primary_entry,
                                                                      'bedrooms': _unit.residential_space.bedrooms,
                                                                      'bathrooms': _unit.residential_space.full_bathrooms,
                                                                      'rent_amount': _unit.rent_amount,
                                                                      'market_rent_amount': _unit.market_rent,
                                                                      'vacate_date': _unit.event.vacate_date,
                                                                      'type': _unit.residential_space.floor_plan.name}
                else:
                    if _unit.residential_space.max_sqft > price_dict[_unit.residential_space.floor_plan.name][
                        'sqft_max']:
                        price_dict[_unit.residential_space.floor_plan.name][
                            'sqft_max'] = _unit.residential_space.max_sqft
                    if _unit.residential_space.min_sqft < price_dict[_unit.residential_space.floor_plan.name][
                        'sqft_min']:
                        price_dict[_unit.residential_space.floor_plan.name][
                            'sqft_min'] = _unit.residential_space.min_sqft

                    if (_status == UnitStatus.VACANT_NOT_LEASE) or (_status == UnitStatus.NTV_AVAILABLE) or (
                            _status == UnitStatus.REHAB) or (_unit.availability == 'True'):
                        if available_date and expire_date:
                            if available_date <= expire_date:
                                price_dict[_unit.residential_space.floor_plan.name]['availability'] += 1

                                if price_dict[_unit.residential_space.floor_plan.name]['price'] == 0:
                                    price_dict[_unit.residential_space.floor_plan.name]['price'] = _unit.price
                                elif price_dict[_unit.residential_space.floor_plan.name]['price'] > _unit.price:
                                    price_dict[_unit.residential_space.floor_plan.name]['price'] = _unit.price

                                _community['vacant_units'][unit_count] = {'name': _unit.name,
                                                                          'square_feet': _unit.residential_space.min_sqft,
                                                                          'floor': _unit.residential_space.level_of_primary_entry,
                                                                          'bedrooms': _unit.residential_space.bedrooms,
                                                                          'bathrooms': _unit.residential_space.full_bathrooms,
                                                                          'rent_amount': _unit.rent_amount,
                                                                          'market_rent_amount': _unit.market_rent,
                                                                          'vacate_date': _unit.event.vacate_date,
                                                                          'type': _unit.residential_space.floor_plan.name}
                        else:
                            price_dict[_unit.residential_space.floor_plan.name]['availability'] += 1

                            if price_dict[_unit.residential_space.floor_plan.name]['price'] == 0:
                                price_dict[_unit.residential_space.floor_plan.name]['price'] = _unit.price
                            elif price_dict[_unit.residential_space.floor_plan.name]['price'] > _unit.price:
                                price_dict[_unit.residential_space.floor_plan.name]['price'] = _unit.price

                if (_status == UnitStatus.VACANT_NOT_LEASE) or (_status == UnitStatus.NTV_AVAILABLE) or (
                        _status == UnitStatus.REHAB) or (_unit.availability == 'True'):
                    if available_date and expire_date:
                        if available_date <= expire_date:
                            _community['vacant_units'][unit_count] = {'name': _unit.name,
                                                                      'square_feet': _unit.residential_space.min_sqft,
                                                                      'floor': _unit.residential_space.level_of_primary_entry,
                                                                      'bedrooms': _unit.residential_space.bedrooms,
                                                                      'bathrooms': _unit.residential_space.full_bathrooms,
                                                                      'rent_amount': _unit.rent_amount,
                                                                      'market_rent_amount': _unit.market_rent,
                                                                      'vacate_date': _unit.event.vacate_date,
                                                                      'type': _unit.residential_space.floor_plan.name}
                            if _unit.residential_space.floor_plan.name == "A6":
                                logging.info("available unit_name in A6: {}".format(_unit.name))
                    else:
                        _community['vacant_units'][unit_count] = {'name': _unit.name,
                                                                  'square_feet': _unit.residential_space.min_sqft,
                                                                  'floor': _unit.residential_space.level_of_primary_entry,
                                                                  'bedrooms': _unit.residential_space.bedrooms,
                                                                  'bathrooms': _unit.residential_space.full_bathrooms,
                                                                  'rent_amount': _unit.rent_amount,
                                                                  'market_rent_amount': _unit.market_rent,
                                                                  'vacate_date': _unit.event.vacate_date,
                                                                  'type': _unit.residential_space.floor_plan.name}
                        if _unit.residential_space.floor_plan.name == "A6":
                            logging.info("available unit_name in A6: {}".format(_unit.name))
            # check square feet value.
            for key in price_dict.keys():
                min = price_dict[key]['sqft_min']
                max = price_dict[key]['sqft_max']

                del price_dict[key]['sqft_min']
                del price_dict[key]['sqft_max']

                price_dict[key]['sqft'] = str(min) if min == max else str(min) + ' - ' + str(max)

            _community['availability'] = list(price_dict.values())

        return result
