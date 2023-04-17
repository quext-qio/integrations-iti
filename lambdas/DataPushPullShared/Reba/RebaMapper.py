from datetime import date

from DataPushPullShared.Model.CommonStructure import CommonStructure


def serializeObject(obj):
    if isinstance(obj, date):
        serial = obj.isoformat()
        return serial
    return obj.__dict__


class RebaMapper:
    @staticmethod
    def setUnitDetails(data: CommonStructure):
        result = []
        communityData = data.data.community
        for item in communityData.keys():
            _community = {'PropertyName': communityData[item].short_name, 'units': []}
            for key in communityData[item].units.keys():
                _unit = {
                    'UnitNumber': communityData[item].units[key].name,
                    'SquareFeet': communityData[item].units[key].residential_space.sqft,
                    'FloorNumber': communityData[item].units[key].residential_space.level_of_primary_entry,
                    'BedroomCount': communityData[item].units[key].residential_space.bedrooms,
                    'BathroomCount': float(communityData[item].units[key].residential_space.full_bathrooms),
                    'HalfBathroomCount': float(communityData[item].units[key].residential_space.half_bathrooms)
                }
                _community['units'].append(_unit)
            result.append(_community)
        return result

    @staticmethod
    def setAmenityDetails(data: CommonStructure):
        result = []
        communityData = data.data.community
        for communityKey in communityData.keys():
            _community = {'PropertyName': communityData[communityKey].short_name, 'units': []}
            for unitKey in communityData[communityKey].units:
                _unit = {'UnitNumber': communityData[communityKey].units[unitKey].name, 'amenity': []}
                _community['units'].append(_unit)
                for amenity in communityData[communityKey].units[unitKey].unit_amenities:
                    _amenity = {
                        'AmenityName': amenity.amenity_id,
                        'AmenityValue': amenity.added_rent_value
                    }
                    _unit['amenity'].append(_amenity)
            result.append(_community)
        return result

    @staticmethod
    def setCommunityDetails(data: CommonStructure):
        result = []
        communityData = data.data.community
        for item in communityData.keys():
            _data = {'PropertyName': communityData[item].short_name,
                     'Address1': communityData[item].property.physical_location.address,
                     'Address2': communityData[item].property.physical_location.address2,
                     'City': communityData[item].property.physical_location.city,
                     'StateProvinceCode': communityData[item].property.physical_location.state,
                     'PostalCode': communityData[item].property.physical_location.postal_code,
                     'Phone': communityData[item].contact_methods.phone,
                     'EmailAddress': communityData[item].contact_methods.email,
                     'UnitCount': communityData[item].unit_count}
            result.append(_data)
        return result