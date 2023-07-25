import datetime
import re
from enum import Enum

from cerberus import Validator

from PeriodicShared.Config.Config import periodic_config_development, periodic_config_production
from PeriodicShared.Model.Periodic import EnvironmentType
from PeriodicShared.Model.PeriodicResponse import BaseResponse
from PeriodicShared.Utilities.PeriodicConstants import PeriodicConstants


class Operation(Enum):
    INPUT = 1,
    OUTPUT = 2,
    REQUEST_METHOD = 3


class Schema(Enum):
    NONE = 0,
    CREATE_COMMUNITY = 1,
    PLATFORM_DATA = 2,
    CREATE_BOOKABLE = 3,
    CREATE_RESOURCE = 4,
    CREATE_MESSAGING_NOTIFICATION = 5,
    UPDATE_RESOURCE = 6,
    DELETE_RESOURCE = 7,
    GET_RESOURCE = 8,
    UPDATE_BOOKABLE = 9,
    GET_BOOKABLE = 10,
    UPDATE_COMMUNITY = 11,
    DELETE_BOOKABLE = 12,
    DELETE_COMMUNITY = 13,
    GET_COMMUNITY = 14


class PlatformData:
    communityUUID: str
    customerUUID: str


class DataValidation:
    @staticmethod
    def getPlatformRequestData(_data, _purpose: str):
        param = {}
        _isValid, _error = Validate.schema(Schema.PLATFORM_DATA, _data)
        if _isValid:
            param = {
                PeriodicConstants.COMMUNITY_UUID: _data.communityUUID,
                PeriodicConstants.CUSTOMER_UUID: _data.customerUUID,
                PeriodicConstants.PURPOSE: _purpose
            }

        return param, _error


def constructAvailabilityObj(_data: list, day: str):
    res = []
    for item in _data:
        if len(item['start']) > 0 and len(item['end']) > 0:
            keys = ['startday', 'starthour', 'startminute', 'startsecond',
                    'endday', 'endhour', 'endminute', 'endsecond']

            values = [day]
            values += list(map(int, item['start'].split(':')))
            values.append(day)
            values += list(map(int, item['end'].split(':')))
            res.append(dict(zip(keys, values)))
    return res


def validateCommunityCustomer(_community, _customer):
    validPattern = re.compile(ValidationConstants.UUID_REGEX)
    isValid = True
    response = BaseResponse()

    if not validPattern.match(_community):
        isValid = False
        response.error[PeriodicConstants.COMMUNITY_UUID] = 'Invalid Community UUID'
    if not validPattern.match(_customer):
        isValid = False
        response.error[PeriodicConstants.CUSTOMER_UUID] = 'Invalid Customer UUID'
    return isValid, response


def validatePlatformResponseData(_responseCode):
    _error = BaseResponse()
    if _responseCode == 200:
        return True, _error
    elif _responseCode == 404:
        _error.error[PeriodicConstants.PLATFORM_DATA] = 'Invalid Platform Data'
        return False, _error
    elif _responseCode == 400:
        _error.error[PeriodicConstants.PLATFORM_DATA] = 'Invalid Platform Data'
        return False, _error
    else:
        _error.error[PeriodicConstants.PLATFORM_DATA] = 'Invalid Platform Data'
        return False, _error


def convertPeriodicAvailability(_data: list):
    availability = {
        "monday": [],
        "friday": [],
        "saturday": [],
        "sunday": [],
        "thursday": [],
        "tuesday": [],
        "wednesday": []
    }
    for item in _data:
        availability[item['startday']].append({
            'start': str((datetime.datetime.strptime(
                str(item['starthour']) + ":" + str(item['startminute']) + ":" + str(item['startsecond']),
                "%H:%M:%S"))).split(' ')[1],
            'end': str((datetime.datetime.strptime(
                str(item['endhour']) + ":" + str(item['endminute']) + ":" + str(item['endsecond']),
                "%H:%M:%S"))).split(' ')[1]
        })
    return availability


def validateAvailability(_data: dict, key: str):
    if validateAvailabilityObj(_data[PeriodicConstants.MONDAY]) and \
            validateAvailabilityObj(_data[PeriodicConstants.TUESDAY]) and \
            validateAvailabilityObj(_data[PeriodicConstants.WEDNESDAY]) and \
            validateAvailabilityObj(_data[PeriodicConstants.THURSDAY]) and \
            validateAvailabilityObj(_data[PeriodicConstants.FRIDAY]) and \
            validateAvailabilityObj(_data[PeriodicConstants.SATURDAY]) and \
            validateAvailabilityObj(_data[PeriodicConstants.SUNDAY]):
        return True, {}
    return False, {key: "end must be greater than start"}


def validateAvailabilityObj(_data: list):
    for item in _data:
        start = datetime.datetime.strptime(item['start'], "%H:%M:%S")
        end = datetime.datetime.strptime(item['end'], "%H:%M:%S")
        if start > end:
            return False
    return True


def getPlatformConfig(_env: EnvironmentType):
    """
        @desc: this method will check for the _type value and _env. Return platform config
    """
    if _env == EnvironmentType.DEVELOPMENT:
        return periodic_config_development
    elif _env == EnvironmentType.PRODUCTION:
        return periodic_config_production
    return {}


class Validate:
    @staticmethod
    def formatError(obj, key, clipBoard, duplicateKey):
        """ Format the error dict into clipBoard"""
        if isinstance(obj, dict):
            return {k: Validate.formatError(v, k, clipBoard, duplicateKey) for k, v in obj.items()}
        elif isinstance(obj, list) and len(obj) == 1 and isinstance(obj[0], str):
            if key not in duplicateKey:
                if "regex" in obj[0] or "missing" in obj[0]:
                    clipBoard.update({key: 'invalid ' + key})
                    duplicateKey.append(key)
                    return obj[0]
                else:
                    clipBoard.update({key: obj[0]})
                    duplicateKey.append(key)
                    return obj[0]

        elif isinstance(obj, list) and len(obj) == 1 and isinstance(obj[0], dict):
            return Validate.formatError(obj[0], None, clipBoard, duplicateKey)
        elif isinstance(obj, list) and len(obj) > 1:
            return {k: Validate.formatError(v, k, clipBoard, duplicateKey) for k, v in obj}

    @staticmethod
    def schema(_schemaType: Schema, _data: dict):
        """ Validate the _data schema with _schemaType and return appropriate validation status and validation errors"""
        v = Validator()
        isValid = v.validate(_data, Validation_Schema[_schemaType])
        error = {}
        Validate.formatError(v.errors, None, error, [])
        return isValid, error


class ValidationConstants:
    UUID_REGEX = "[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"
    CHARACTER_REGEX = "^[A-Za-z -]+$"
    CITY_REGEX = "^[A-Za-z '-]+$"
    EMAIL_REGEX = "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    PHONE_REGEX = "^(?:(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$"
    STREET_ADDRESS_REGEX = "^[0-9A-Za-z -]+$"
    US_STATES = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY',
                 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND',
                 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC',
                 'MP', 'PW', 'PR', 'VI']
    COUNTRY = ['USA']
    TIMEZONE = ['Africa/Abidjan', 'Africa/Accra', 'Africa/Addis_Ababa', 'Africa/Algiers', 'Africa/Asmara',
                'Africa/Asmera', 'Africa/Bamako', 'Africa/Bangui', 'Africa/Banjul', 'Africa/Bissau', 'Africa/Blantyre',
                'Africa/Brazzaville', 'Africa/Bujumbura', 'Africa/Cairo', 'Africa/Casablanca', 'Africa/Ceuta',
                'Africa/Conakry', 'Africa/Dakar', 'Africa/Dar_es_Salaam', 'Africa/Djibouti', 'Africa/Douala',
                'Africa/El_Aaiun', 'Africa/Freetown', 'Africa/Gaborone', 'Africa/Harare', 'Africa/Johannesburg',
                'Africa/Juba', 'Africa/Kampala', 'Africa/Khartoum', 'Africa/Kigali', 'Africa/Kinshasa', 'Africa/Lagos',
                'Africa/Libreville', 'Africa/Lome', 'Africa/Luanda', 'Africa/Lubumbashi', 'Africa/Lusaka',
                'Africa/Malabo', 'Africa/Maputo', 'Africa/Maseru', 'Africa/Mbabane', 'Africa/Mogadishu',
                'Africa/Monrovia', 'Africa/Nairobi', 'Africa/Ndjamena', 'Africa/Niamey', 'Africa/Nouakchott',
                'Africa/Ouagadougou', 'Africa/Porto-Novo', 'Africa/Sao_Tome', 'Africa/Timbuktu', 'Africa/Tripoli',
                'Africa/Tunis', 'Africa/Windhoek', 'America/Adak', 'America/Anchorage', 'America/Anguilla',
                'America/Antigua', 'America/Araguaina', 'America/Argentina/Buenos_Aires', 'America/Argentina/Catamarca',
                'America/Argentina/ComodRivadavia', 'America/Argentina/Cordoba', 'America/Argentina/Jujuy',
                'America/Argentina/La_Rioja', 'America/Argentina/Mendoza', 'America/Argentina/Rio_Gallegos',
                'America/Argentina/Salta', 'America/Argentina/San_Juan', 'America/Argentina/San_Luis',
                'America/Argentina/Tucuman', 'America/Argentina/Ushuaia', 'America/Aruba', 'America/Asuncion',
                'America/Atikokan', 'America/Atka', 'America/Bahia', 'America/Bahia_Banderas', 'America/Barbados',
                'America/Belem', 'America/Belize', 'America/Blanc-Sablon', 'America/Boa_Vista', 'America/Bogota',
                'America/Boise', 'America/Buenos_Aires', 'America/Cambridge_Bay', 'America/Campo_Grande',
                'America/Cancun', 'America/Caracas', 'America/Catamarca', 'America/Cayenne', 'America/Cayman',
                'America/Chicago', 'America/Chihuahua', 'America/Coral_Harbour', 'America/Cordoba',
                'America/Costa_Rica', 'America/Creston', 'America/Cuiaba', 'America/Curacao', 'America/Danmarkshavn',
                'America/Dawson', 'America/Dawson_Creek', 'America/Denver', 'America/Detroit', 'America/Dominica',
                'America/Edmonton', 'America/Eirunepe', 'America/El_Salvador', 'America/Ensenada',
                'America/Fort_Nelson', 'America/Fort_Wayne', 'America/Fortaleza', 'America/Glace_Bay',
                'America/Godthab', 'America/Goose_Bay', 'America/Grand_Turk', 'America/Grenada', 'America/Guadeloupe',
                'America/Guatemala', 'America/Guayaquil', 'America/Guyana', 'America/Halifax', 'America/Havana',
                'America/Hermosillo', 'America/Indiana/Indianapolis', 'America/Indiana/Knox', 'America/Indiana/Marengo',
                'America/Indiana/Petersburg', 'America/Indiana/Tell_City', 'America/Indiana/Vevay',
                'America/Indiana/Vincennes', 'America/Indiana/Winamac', 'America/Indianapolis', 'America/Inuvik',
                'America/Iqaluit', 'America/Jamaica', 'America/Jujuy', 'America/Juneau', 'America/Kentucky/Louisville',
                'America/Kentucky/Monticello', 'America/Knox_IN', 'America/Kralendijk', 'America/La_Paz',
                'America/Lima', 'America/Los_Angeles', 'America/Louisville', 'America/Lower_Princes', 'America/Maceio',
                'America/Managua', 'America/Manaus', 'America/Marigot', 'America/Martinique', 'America/Matamoros',
                'America/Mazatlan', 'America/Mendoza', 'America/Menominee', 'America/Merida', 'America/Metlakatla',
                'America/Mexico_City', 'America/Miquelon', 'America/Moncton', 'America/Monterrey', 'America/Montevideo',
                'America/Montreal', 'America/Montserrat', 'America/Nassau', 'America/New_York', 'America/Nipigon',
                'America/Nome', 'America/Noronha', 'America/North_Dakota/Beulah', 'America/North_Dakota/Center',
                'America/North_Dakota/New_Salem', 'America/Nuuk', 'America/Ojinaga', 'America/Panama',
                'America/Pangnirtung', 'America/Paramaribo', 'America/Phoenix', 'America/Port-au-Prince',
                'America/Port_of_Spain', 'America/Porto_Acre', 'America/Porto_Velho', 'America/Puerto_Rico',
                'America/Punta_Arenas', 'America/Rainy_River', 'America/Rankin_Inlet', 'America/Recife',
                'America/Regina', 'America/Resolute', 'America/Rio_Branco', 'America/Rosario', 'America/Santa_Isabel',
                'America/Santarem', 'America/Santiago', 'America/Santo_Domingo', 'America/Sao_Paulo',
                'America/Scoresbysund', 'America/Shiprock', 'America/Sitka', 'America/St_Barthelemy',
                'America/St_Johns', 'America/St_Kitts', 'America/St_Lucia', 'America/St_Thomas', 'America/St_Vincent',
                'America/Swift_Current', 'America/Tegucigalpa', 'America/Thule', 'America/Thunder_Bay',
                'America/Tijuana', 'America/Toronto', 'America/Tortola', 'America/Vancouver', 'America/Virgin',
                'America/Whitehorse', 'America/Winnipeg', 'America/Yakutat', 'America/Yellowknife', 'Antarctica/Casey',
                'Antarctica/Davis', 'Antarctica/DumontDUrville', 'Antarctica/Macquarie', 'Antarctica/Mawson',
                'Antarctica/McMurdo', 'Antarctica/Palmer', 'Antarctica/Rothera', 'Antarctica/South_Pole',
                'Antarctica/Syowa', 'Antarctica/Troll', 'Antarctica/Vostok', 'Arctic/Longyearbyen', 'Asia/Aden',
                'Asia/Almaty', 'Asia/Amman', 'Asia/Anadyr', 'Asia/Aqtau', 'Asia/Aqtobe', 'Asia/Ashgabat',
                'Asia/Ashkhabad', 'Asia/Atyrau', 'Asia/Baghdad', 'Asia/Bahrain', 'Asia/Baku', 'Asia/Bangkok',
                'Asia/Barnaul', 'Asia/Beirut', 'Asia/Bishkek', 'Asia/Brunei', 'Asia/Calcutta', 'Asia/Chita',
                'Asia/Choibalsan', 'Asia/Chongqing', 'Asia/Chungking', 'Asia/Colombo', 'Asia/Dacca', 'Asia/Damascus',
                'Asia/Dhaka', 'Asia/Dili', 'Asia/Dubai', 'Asia/Dushanbe', 'Asia/Famagusta', 'Asia/Gaza', 'Asia/Harbin',
                'Asia/Hebron', 'Asia/Ho_Chi_Minh', 'Asia/Hong_Kong', 'Asia/Hovd', 'Asia/Irkutsk', 'Asia/Istanbul',
                'Asia/Jakarta', 'Asia/Jayapura', 'Asia/Jerusalem', 'Asia/Kabul', 'Asia/Kamchatka', 'Asia/Karachi',
                'Asia/Kashgar', 'Asia/Kathmandu', 'Asia/Katmandu', 'Asia/Khandyga', 'Asia/Kolkata', 'Asia/Krasnoyarsk',
                'Asia/Kuala_Lumpur', 'Asia/Kuching', 'Asia/Kuwait', 'Asia/Macao', 'Asia/Macau', 'Asia/Magadan',
                'Asia/Makassar', 'Asia/Manila', 'Asia/Muscat', 'Asia/Nicosia', 'Asia/Novokuznetsk', 'Asia/Novosibirsk',
                'Asia/Omsk', 'Asia/Oral', 'Asia/Phnom_Penh', 'Asia/Pontianak', 'Asia/Pyongyang', 'Asia/Qatar',
                'Asia/Qostanay', 'Asia/Qyzylorda', 'Asia/Rangoon', 'Asia/Riyadh', 'Asia/Saigon', 'Asia/Sakhalin',
                'Asia/Samarkand', 'Asia/Seoul', 'Asia/Shanghai', 'Asia/Singapore', 'Asia/Srednekolymsk', 'Asia/Taipei',
                'Asia/Tashkent', 'Asia/Tbilisi', 'Asia/Tehran', 'Asia/Tel_Aviv', 'Asia/Thimbu', 'Asia/Thimphu',
                'Asia/Tokyo', 'Asia/Tomsk', 'Asia/Ujung_Pandang', 'Asia/Ulaanbaatar', 'Asia/Ulan_Bator', 'Asia/Urumqi',
                'Asia/Ust-Nera', 'Asia/Vientiane', 'Asia/Vladivostok', 'Asia/Yakutsk', 'Asia/Yangon',
                'Asia/Yekaterinburg', 'Asia/Yerevan', 'Atlantic/Azores', 'Atlantic/Bermuda', 'Atlantic/Canary',
                'Atlantic/Cape_Verde', 'Atlantic/Faeroe', 'Atlantic/Faroe', 'Atlantic/Jan_Mayen', 'Atlantic/Madeira',
                'Atlantic/Reykjavik', 'Atlantic/South_Georgia', 'Atlantic/St_Helena', 'Atlantic/Stanley',
                'Australia/ACT', 'Australia/Adelaide', 'Australia/Brisbane', 'Australia/Broken_Hill',
                'Australia/Canberra', 'Australia/Currie', 'Australia/Darwin', 'Australia/Eucla', 'Australia/Hobart',
                'Australia/LHI', 'Australia/Lindeman', 'Australia/Lord_Howe', 'Australia/Melbourne', 'Australia/NSW',
                'Australia/North', 'Australia/Perth', 'Australia/Queensland', 'Australia/South', 'Australia/Sydney',
                'Australia/Tasmania', 'Australia/Victoria', 'Australia/West', 'Australia/Yancowinna', 'Brazil/Acre',
                'Brazil/DeNoronha', 'Brazil/East', 'Brazil/West', 'CET', 'CST6CDT', 'Canada/Atlantic', 'Canada/Central',
                'Canada/Eastern', 'Canada/Mountain', 'Canada/Newfoundland', 'Canada/Pacific', 'Canada/Saskatchewan',
                'Canada/Yukon', 'Chile/Continental', 'Chile/EasterIsland', 'Cuba', 'EET', 'EST', 'EST5EDT', 'Egypt',
                'Eire', 'Etc/GMT', 'Etc/GMT+0', 'Etc/GMT+1', 'Etc/GMT+10', 'Etc/GMT+11', 'Etc/GMT+12', 'Etc/GMT+2',
                'Etc/GMT+3', 'Etc/GMT+4', 'Etc/GMT+5', 'Etc/GMT+6', 'Etc/GMT+7', 'Etc/GMT+8', 'Etc/GMT+9', 'Etc/GMT-0',
                'Etc/GMT-1', 'Etc/GMT-10', 'Etc/GMT-11', 'Etc/GMT-12', 'Etc/GMT-13', 'Etc/GMT-14', 'Etc/GMT-2',
                'Etc/GMT-3', 'Etc/GMT-4', 'Etc/GMT-5', 'Etc/GMT-6', 'Etc/GMT-7', 'Etc/GMT-8', 'Etc/GMT-9', 'Etc/GMT0',
                'Etc/Greenwich', 'Etc/UCT', 'Etc/UTC', 'Etc/Universal', 'Etc/Zulu', 'Europe/Amsterdam',
                'Europe/Andorra', 'Europe/Astrakhan', 'Europe/Athens', 'Europe/Belfast', 'Europe/Belgrade',
                'Europe/Berlin', 'Europe/Bratislava', 'Europe/Brussels', 'Europe/Bucharest', 'Europe/Budapest',
                'Europe/Busingen', 'Europe/Chisinau', 'Europe/Copenhagen', 'Europe/Dublin', 'Europe/Gibraltar',
                'Europe/Guernsey', 'Europe/Helsinki', 'Europe/Isle_of_Man', 'Europe/Istanbul', 'Europe/Jersey',
                'Europe/Kaliningrad', 'Europe/Kiev', 'Europe/Kirov', 'Europe/Lisbon', 'Europe/Ljubljana',
                'Europe/London', 'Europe/Luxembourg', 'Europe/Madrid', 'Europe/Malta', 'Europe/Mariehamn',
                'Europe/Minsk', 'Europe/Monaco', 'Europe/Moscow', 'Europe/Nicosia', 'Europe/Oslo', 'Europe/Paris',
                'Europe/Podgorica', 'Europe/Prague', 'Europe/Riga', 'Europe/Rome', 'Europe/Samara', 'Europe/San_Marino',
                'Europe/Sarajevo', 'Europe/Saratov', 'Europe/Simferopol', 'Europe/Skopje', 'Europe/Sofia',
                'Europe/Stockholm', 'Europe/Tallinn', 'Europe/Tirane', 'Europe/Tiraspol', 'Europe/Ulyanovsk',
                'Europe/Uzhgorod', 'Europe/Vaduz', 'Europe/Vatican', 'Europe/Vienna', 'Europe/Vilnius',
                'Europe/Volgograd', 'Europe/Warsaw', 'Europe/Zagreb', 'Europe/Zaporozhye', 'Europe/Zurich', 'GB',
                'GB-Eire', 'GMT', 'GMT+0', 'GMT-0', 'GMT0', 'Greenwich', 'HST', 'Hongkong', 'Iceland',
                'Indian/Antananarivo', 'Indian/Chagos', 'Indian/Christmas', 'Indian/Cocos', 'Indian/Comoro',
                'Indian/Kerguelen', 'Indian/Mahe', 'Indian/Maldives', 'Indian/Mauritius', 'Indian/Mayotte',
                'Indian/Reunion', 'Iran', 'Israel', 'Jamaica', 'Japan', 'Kwajalein', 'Libya', 'MET', 'MST', 'MST7MDT',
                'Mexico/BajaNorte', 'Mexico/BajaSur', 'Mexico/General', 'NZ', 'NZ-CHAT', 'Navajo', 'PRC', 'PST8PDT',
                'Pacific/Apia', 'Pacific/Auckland', 'Pacific/Bougainville', 'Pacific/Chatham', 'Pacific/Chuuk',
                'Pacific/Easter', 'Pacific/Efate', 'Pacific/Enderbury', 'Pacific/Fakaofo', 'Pacific/Fiji',
                'Pacific/Funafuti', 'Pacific/Galapagos', 'Pacific/Gambier', 'Pacific/Guadalcanal', 'Pacific/Guam',
                'Pacific/Honolulu', 'Pacific/Johnston', 'Pacific/Kiritimati', 'Pacific/Kosrae', 'Pacific/Kwajalein',
                'Pacific/Majuro', 'Pacific/Marquesas', 'Pacific/Midway', 'Pacific/Nauru', 'Pacific/Niue',
                'Pacific/Norfolk', 'Pacific/Noumea', 'Pacific/Pago_Pago', 'Pacific/Palau', 'Pacific/Pitcairn',
                'Pacific/Pohnpei', 'Pacific/Ponape', 'Pacific/Port_Moresby', 'Pacific/Rarotonga', 'Pacific/Saipan',
                'Pacific/Samoa', 'Pacific/Tahiti', 'Pacific/Tarawa', 'Pacific/Tongatapu', 'Pacific/Truk',
                'Pacific/Wake', 'Pacific/Wallis', 'Pacific/Yap', 'Poland', 'Portugal', 'ROC', 'ROK', 'Singapore',
                'Turkey', 'UCT', 'US/Alaska', 'US/Aleutian', 'US/Arizona', 'US/Central', 'US/East-Indiana',
                'US/Eastern', 'US/Hawaii', 'US/Indiana-Starke', 'US/Michigan', 'US/Mountain', 'US/Pacific', 'US/Samoa',
                'UTC', 'Universal', 'W-SU', 'WET', 'Zulu']
    POSTAL_CODE_REGEX = "^[0-9]{5}(?:-[0-9]{4})?$"
    TIME_REGEX = "^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$"


Schema_ADDRESS = {'streetAddress': {'required': True,
                                    'type': 'string',
                                    'empty': True,
                                    'regex': ValidationConstants.STREET_ADDRESS_REGEX},
                  'city': {'required': True,
                           'type': 'string',
                           'empty': True,
                           'regex': ValidationConstants.CITY_REGEX},
                  'state': {'required': True,
                            'type': 'string',
                            'allowed': ValidationConstants.US_STATES},
                  'country': {'required': True,
                              'type': 'string',
                              'allowed': ValidationConstants.COUNTRY},
                  'postalCode': {'required': True,
                                 'type': 'string',
                                 'empty': True,
                                 'regex': ValidationConstants.POSTAL_CODE_REGEX},
                  }

Schema_Time_Object = {'type': 'dict',
                      'required': True,
                      'schema': {'start': {'required': True,
                                           'type': 'string',
                                           'empty': False,
                                           'regex': ValidationConstants.TIME_REGEX
                                           },
                                 'end': {'required': True,
                                         'type': 'string',
                                         'empty': False,
                                         'regex': ValidationConstants.TIME_REGEX
                                         }
                                 }
                      }

Schema_Availability = {'monday': {'required': False,
                                  'type': 'list',
                                  'schema': Schema_Time_Object
                                  },
                       'tuesday': {'required': False,
                                   'type': 'list',
                                   'schema': Schema_Time_Object
                                   },
                       'wednesday': {'required': False,
                                     'type': 'list',
                                     'schema': Schema_Time_Object
                                     },
                       'thursday': {'required': False,
                                    'type': 'list',
                                    'schema': Schema_Time_Object
                                    },
                       'friday': {'required': False,
                                  'type': 'list',
                                  'schema': Schema_Time_Object
                                  },
                       'saturday': {'required': False,
                                    'type': 'list',
                                    'schema': Schema_Time_Object
                                    },
                       'sunday': {'required': False,
                                  'type': 'list',
                                  'schema': Schema_Time_Object
                                  }
                       }

Validation_Schema = {
    Schema.NONE: None,
    Schema.PLATFORM_DATA: {
        'communityUUID': {'required': True,
                          'type': 'string',
                          'regex': ValidationConstants.UUID_REGEX},
        'customerUUID': {'required': True,
                         'type': 'string',
                         'regex': ValidationConstants.UUID_REGEX},
        'purpose': {'required': True,
                    'type': 'string',
                    'empty': False}
    },
    Schema.CREATE_COMMUNITY: {
        'communityData': {'required': True,
                          'type': 'dict',
                          'schema': {
                              'communityName': {'required': True,
                                                'type': 'string',
                                                'regex': ValidationConstants.CHARACTER_REGEX},
                              'subDomain': {'required': True,
                                            'type': 'string',
                                            'regex': ValidationConstants.CHARACTER_REGEX},
                              'timezone': {'required': True,
                                           'type': 'string',
                                           'allowed': ValidationConstants.TIMEZONE},
                              'description': {'required': False,
                                              'type': 'string'},
                              'internalCode': {'required': False,
                                               'type': 'string'},
                              'email': {'required': True,
                                        'type': 'string',
                                        'regex': ValidationConstants.EMAIL_REGEX},
                              'replyEmail': {'required': True,
                                             'type': 'string',
                                             'regex': ValidationConstants.EMAIL_REGEX},
                              'website': {'required': False,
                                          'type': 'string'},
                              'phone': {'required': True,
                                        'type': 'string',
                                        'regex': ValidationConstants.PHONE_REGEX},
                              'address': {'required': True,
                                          'type': 'dict',
                                          'schema': {'streetAddress': {'required': True,
                                                                       'type': 'string',
                                                                       'empty': True,
                                                                       'regex': ValidationConstants.STREET_ADDRESS_REGEX},
                                                     'city': {'required': True,
                                                              'type': 'string',
                                                              'empty': True,
                                                              'regex': ValidationConstants.CITY_REGEX},
                                                     'state': {'required': True,
                                                               'type': 'string',
                                                               'allowed': ValidationConstants.US_STATES},
                                                     'country': {'required': True,
                                                                 'type': 'string',
                                                                 'allowed': ValidationConstants.COUNTRY},
                                                     'postalCode': {'required': True,
                                                                    'type': 'string',
                                                                    'empty': True,
                                                                    'regex': ValidationConstants.POSTAL_CODE_REGEX},
                                                     }},
                              'enableNotification': {'required': False,
                                                     'empty': True,
                                                     'type': 'boolean'},
                              'facebookURL': {'required': False,
                                              'type': 'string'},
                              'twitterURL': {'required': False,
                                             'type': 'string'},
                              'instagramURL': {'required': False,
                                               'type': 'string'},
                              'pinterestURL': {'required': False,
                                               'type': 'string'},
                              'availability': {'required': True,
                                               'type': 'dict',
                                               'schema': Schema_Availability
                                               }}},
        'bookableData': {'required': True,
                         'type': 'dict',
                         'schema': {'appointmentDuration': {'required': False,
                                                            'type': 'integer'},
                                    'appointmentFrequency': {'required': False,
                                                             'type': 'integer'},
                                    'availability': {'required': True,
                                                     'type': 'dict',
                                                     'schema': Schema_Availability
                                                     }
                                    }
                         },
        'resourceData': {'required': True,
                         'type': 'list',
                         'schema':
                             {'required': True,
                              'type': 'dict',
                              'schema': {
                                  'phone': {'required': False,
                                            'type': 'string'},
                                  'name': {'required': True,
                                           'type': 'string',
                                           'regex': ValidationConstants.CHARACTER_REGEX},
                                  'timezone': {'required': True,
                                               'type': 'string',
                                               'allowed': ValidationConstants.TIMEZONE},
                                  'url': {'required': False,
                                          'type': 'string'},
                                  'availability': {'required': True,
                                                   'type': 'dict',
                                                   'schema': Schema_Availability
                                                   }
                              }
                              }
                         }
    },
    Schema.CREATE_BOOKABLE: {'appointmentDuration': {'required': False,
                                                     'type': 'integer'},
                             'appointmentFrequency': {'required': False,
                                                      'type': 'integer'},
                             'availability': {'required': True,
                                              'type': 'dict',
                                              'schema': Schema_Availability
                                              },
                             'communityName': {'required': True,
                                               'type': 'string',
                                               'regex': ValidationConstants.CHARACTER_REGEX},
                             'senderEmail': {'required': True,
                                             'type': 'string',
                                             'regex': ValidationConstants.EMAIL_REGEX},
                             'communityID': {'required': True,
                                             'type': 'string',
                                             'regex': ValidationConstants.CHARACTER_REGEX}
                             },
    Schema.CREATE_RESOURCE: {'phone': {'required': False,
                                       'type': 'string'},
                             'communityID': {'required': True,
                                             'type': 'string',
                                             'empty': False},
                             'name': {'required': True,
                                      'type': 'string',
                                      'regex': ValidationConstants.CHARACTER_REGEX},
                             'timezone': {'required': True,
                                          'type': 'string'},
                             'url': {'required': False,
                                     'type': 'string'},
                             'availability': {'required': True,
                                              'type': 'dict',
                                              'schema': Schema_Availability
                                              }
                             },
    Schema.UPDATE_RESOURCE: {'id': {'required': True,
                                    'type': 'string',
                                    'empty': False},
                             'phone': {'required': False,
                                       'type': 'string',
                                       'empty': False},
                             'name': {'required': False,
                                      'type': 'string',
                                      'empty': False,
                                      'regex': ValidationConstants.CHARACTER_REGEX},
                             'timezone': {'required': False,
                                          'type': 'string',
                                          'allowed': ValidationConstants.TIMEZONE},
                             'url': {'required': False,
                                     'type': 'string',
                                     'empty': False},
                             'availability': {'required': False,
                                              'type': 'dict',
                                              'empty': False,
                                              'schema': Schema_Availability
                                              }
                             },
    Schema.DELETE_RESOURCE: {'id': {'required': True,
                                    'type': 'string',
                                    'empty': False
                                    },
                             'communityID': {'required': True,
                                             'type': 'string',
                                             'empty': False},
                             },
    Schema.GET_RESOURCE: {'communityID': {'required': True,
                                          'type': 'string',
                                          'empty': False},
                          },
    Schema.GET_BOOKABLE: {'communityID': {'required': True,
                                          'type': 'string',
                                          'empty': False},
                          },
    Schema.UPDATE_BOOKABLE: {'id': {'required': True,
                                    'type': 'string',
                                    'empty': False},
                             'name': {'required': False,
                                      'type': 'string',
                                      'empty': False},
                             'appointmentDuration': {'required': False,
                                                     'type': 'integer',
                                                     'empty': False},
                             'appointmentFrequency': {'required': False,
                                                      'type': 'integer',
                                                      'empty': False},
                             'availability': {'required': False,
                                              'type': 'dict',
                                              'empty': False,
                                              'schema': Schema_Availability
                                              },
                             'resourceID': {'required': False,
                                            'type': 'list',
                                            'empty': False},
                             },
    Schema.UPDATE_COMMUNITY: {'communityName': {'required': False,
                                                'type': 'string',
                                                'empty': False,
                                                'regex': ValidationConstants.CHARACTER_REGEX},
                              'subDomain': {'required': True,
                                            'type': 'string',
                                            'empty': False,
                                            'regex': ValidationConstants.CHARACTER_REGEX},
                              'timezone': {'required': False,
                                           'type': 'string',
                                           'allowed': ValidationConstants.TIMEZONE},
                              'description': {'required': False,
                                              'type': 'string',
                                              'empty': False},
                              'internalCode': {'required': False,
                                               'type': 'string',
                                               'empty': False},
                              'email': {'required': False,
                                        'type': 'string',
                                        'empty': False,
                                        'regex': ValidationConstants.EMAIL_REGEX},
                              'replyEmail': {'required': False,
                                             'type': 'string',
                                             'empty': False,
                                             'regex': ValidationConstants.EMAIL_REGEX},
                              'website': {'required': False,
                                          'type': 'string',
                                          'empty': False, },
                              'phone': {'required': False,
                                        'type': 'string',
                                        'empty': False,
                                        'regex': ValidationConstants.PHONE_REGEX},
                              'address': {'required': False,
                                          'type': 'dict',
                                          'schema': {'streetAddress': {'required': True,
                                                                       'type': 'string',
                                                                       'empty': True,
                                                                       'regex': ValidationConstants.STREET_ADDRESS_REGEX},
                                                     'city': {'required': True,
                                                              'type': 'string',
                                                              'empty': True,
                                                              'regex': ValidationConstants.CITY_REGEX},
                                                     'state': {'required': True,
                                                               'type': 'string',
                                                               'allowed': ValidationConstants.US_STATES},
                                                     'country': {'required': True,
                                                                 'type': 'string',
                                                                 'allowed': ValidationConstants.COUNTRY},
                                                     'postalCode': {'required': True,
                                                                    'type': 'string',
                                                                    'empty': True,
                                                                    'regex': ValidationConstants.POSTAL_CODE_REGEX},
                                                     }},
                              'facebookURL': {'required': False,
                                              'type': 'string',
                                              'empty': False, },
                              'twitterURL': {'required': False,
                                             'type': 'string',
                                             'empty': False, },
                              'instagramURL': {'required': False,
                                               'type': 'string',
                                               'empty': False, },
                              'pinterestURL': {'required': False,
                                               'type': 'string',
                                               'empty': False, },
                              'availability': {'required': False,
                                               'type': 'dict',
                                               'empty': False,
                                               'schema': Schema_Availability
                                               }}
}
