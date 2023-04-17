import datetime
from typing import List
import re
from datetime import date
from TourShared.Utilities.Tour_Constants import Tour_Integration_Constants
from TourShared.Model.Data_Model import Layout_Type, Platform_Type, BasePlatformData, ScheduleTourFormData, \
    TourAvailabilityData


class DataValidation:
    @staticmethod
    def isvalid_string(_field):
        if type(_field) is str and (len(_field) > 0):
            return True
        return False

    @staticmethod
    def get_room_layout_type(_type: str):
        switcher = {
            'NONE': Layout_Type.NONE,
            'ONE_BEDROOM': Layout_Type.ONE_BEDROOM,
            'TWO_BEDROOM': Layout_Type.TWO_BEDROOM,
            'THREE_BEDROOM': Layout_Type.THREE_BEDROOM,
            'FOUR_BEDROOM': Layout_Type.FOUR_BEDROOM,
            'FIVE_BEDROOM': Layout_Type.FIVE_BEDROOM,
            'STUDIO': Layout_Type.STUDIO,
            'LOFT': Layout_Type.LOFT,
            'OTHERS': Layout_Type.OTHERS
        }
        return switcher.get(_type, Layout_Type.NONE)

    @staticmethod
    def serialize_object(obj):
        if isinstance(obj, date):
            serial = obj.isoformat()
            return serial
        return obj.__dict__

    @staticmethod
    def get_valid_room_layout(_layout: List[str]):
        data = []
        for item in _layout:
            data.append(DataValidation.get_room_layout_type(item))
        return data

    @staticmethod
    def isvalid_email_address(_email: str):
        regex_Email = '(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
        valid_Pattern = re.compile(regex_Email)

        if valid_Pattern.match(_email) is not None:
            return True
        return False

    @staticmethod
    def isvalid_phone_number(_phone: str):
        regex_Phone = '^(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$'
        valid_Pattern = re.compile(regex_Phone)

        if len(_phone) > 0:
            if valid_Pattern.match(_phone) is not None:
                return True
            else:
                return False
        return True

    @staticmethod
    def isvalid_datetime_format(_date: str):
        regex_Date = '^\d\d\d\d-(0?[1-9]|1[0-2])-(0?[1-9]|[12][0-9]|3[01]) (00|0[0-9]|1[0-9]|2[0-3]):([0-9]|[0-5][0-9]):([0-9]|[0-5][0-9])$'
        valid_Pattern = re.compile(regex_Date)

        if valid_Pattern.match(_date) is not None:
            return True
        return False

    @staticmethod
    def isvalid_uuid_format(_uuid: str):
        regex_Date = '[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}'
        valid_Pattern = re.compile(regex_Date)

        if valid_Pattern.match(_uuid) is not None:
            return True
        return False

    @staticmethod
    def isvalid_date_format(_date: str):
        regex_Date = '^\d{4}(-|\/)((0[1-9])|(1[0-2]))(-|\/)((0[1-9])|([1-2][0-9])|(3[0-1]))'
        valid_Pattern = re.compile(regex_Date)

        if valid_Pattern.match(_date) is not None:
            try:
                ios_Date_Format = datetime.datetime.strptime(_date, '%Y-%m-%d')
            except:
                return False, ''
            return True, ios_Date_Format
        return False, ''

    @staticmethod
    def get_platform_type(_type: str):
        """
            @desc: this method will check for the _type value and returns the platform type
            @param: _type string which contains platform name (eg: NESTIO, PERIODIC)
            @return: platform type enum value
        """
        switcher = {
            'FUNNEL': Platform_Type.FUNNEL,
            'PERIODIC': Platform_Type.PERIODIC
        }
        return switcher.get(_type, Platform_Type.NONE)

    @staticmethod
    def validate_schedule_tour_formdata(_data: ScheduleTourFormData):
        """
                    @desc: this method will check for the _data and returns the boolean, platform type and
                    error after validating
                    @param: _data dictionary which contains platform name (eg: NESTIO, PERIODIC), appointment
                     information like email,first name,last name,phone number and the start time of the appointment
                    @return: boolean value, platform type enum value, error dictionary
        """
        error = {}
        try:
            if DataValidation.isvalid_email_address(
                    _data.appointmentData.email) and DataValidation.isvalid_datetime_format(
                _data.appointmentData.start) and DataValidation.isvalid_string(_data.appointmentData.firstName) and \
                    DataValidation.isvalid_string(_data.appointmentData.lastName) and \
                    DataValidation.isvalid_phone_number(_data.appointmentData.phone):
                return True, error
            else:
                if not DataValidation.isvalid_string(_data.appointmentData.firstName):
                    error[Tour_Integration_Constants.FIRST_NAME] = 'Invalid First Name'
                if not DataValidation.isvalid_string(_data.appointmentData.lastName):
                    error[Tour_Integration_Constants.LAST_NAME] = 'Invalid Last Name'
                if not DataValidation.isvalid_datetime_format(_data.appointmentData.start):
                    error[Tour_Integration_Constants.START] = 'Invalid Start Date'
                if not DataValidation.isvalid_email_address(_data.appointmentData.email):
                    error[Tour_Integration_Constants.EMAIL] = 'Invalid Email'
                if not DataValidation.isvalid_phone_number(_data.appointmentData.phone):
                    error[Tour_Integration_Constants.PHONE] = 'Invalid Phone Number'
                return False, error
        except:
            if Tour_Integration_Constants.FIRST_NAME not in _data:
                error[Tour_Integration_Constants.FIRST_NAME] = 'Missing First Name'
            if Tour_Integration_Constants.LAST_NAME not in _data:
                error[Tour_Integration_Constants.LAST_NAME] = 'Missing Last Name'
            if Tour_Integration_Constants.START not in _data:
                error[Tour_Integration_Constants.START] = 'Missing Start Date'
            if Tour_Integration_Constants.EMAIL not in _data:
                error[Tour_Integration_Constants.EMAIL] = 'Missing Email'
            if Tour_Integration_Constants.PHONE not in _data:
                error[Tour_Integration_Constants.PHONE] = 'Missing Phone Number'
            return False, error

    @staticmethod
    def validate_schedule_availability_formData(_data: TourAvailabilityData):
        """
                            @desc: this method will check for the _data and returns the boolean, platform type and
                            error after validating
                            @param: _data dictionary which contains platform name (eg: NESTIO, PERIODIC), from and to
                            dates from which tour available time slots should be returned.
                            @return: boolean value, platform type enum value, error dictionary
        """
        error = {}
        try:
            isValid_from_date, from_date = DataValidation.isvalid_date_format(_data.fromDate)
            isValid_to_date, to_date = DataValidation.isvalid_date_format(_data.toDate)

            if isValid_from_date and isValid_to_date:
                if to_date >= from_date:
                    return True, error
                else:
                    error[Tour_Integration_Constants.TO_DATE] = 'To_Date must be greater or equal to From_Date'
                    return False, error
            else:
                if not isValid_from_date and len(_data.fromDate) > 0:
                    error[Tour_Integration_Constants.FROM_DATE] = 'Invalid From_Date Format'
                if not isValid_to_date:
                    error[Tour_Integration_Constants.TO_DATE] = 'Invalid To_Date Format'
                if isValid_from_date and isValid_to_date and to_date < from_date:
                    error[Tour_Integration_Constants.TO_DATE] = 'To_Date must be greater than From_Date'
                return False, error
        except:
            if Tour_Integration_Constants.FROM_DATE not in _data:
                error[Tour_Integration_Constants.FROM_DATE] = 'Missing From_Date'
            if Tour_Integration_Constants.TO_DATE not in _data:
                error[Tour_Integration_Constants.TO_DATE] = 'Missing To_Date'
            return False, error

    @staticmethod
    def validate_platform_data(data: BasePlatformData):
        error = {}
        try:
            if DataValidation.isvalid_uuid_format(data.communityUUID) and DataValidation.isvalid_uuid_format(
                    data.customerUUID):
                return True, error
            else:
                if not DataValidation.isvalid_uuid_format(data.communityUUID):
                    error[Tour_Integration_Constants.COMMUNITY_UUID] = 'Invalid Community UUID'
                if not DataValidation.isvalid_uuid_format(data.customerUUID):
                    error[Tour_Integration_Constants.CUSTOMER_UUID] = 'Invalid Customer UUID'
                return False, error
        except:
            if Tour_Integration_Constants.COMMUNITY_UUID not in data:
                error[Tour_Integration_Constants.COMMUNITY_UUID] = 'Missing Community UUID'
            if Tour_Integration_Constants.CUSTOMER_UUID not in data:
                error[Tour_Integration_Constants.CUSTOMER_UUID] = 'Missing Customer UUID'
            return False, error

    @staticmethod
    def get_platform_request_data(data: BasePlatformData, purpose: str):
        error = {}
        param = {}
        _isValid, _error = DataValidation.validate_platform_data(data)
        if _isValid:
            param = {
                Tour_Integration_Constants.COMMUNITY_UUID: data.communityUUID,
                Tour_Integration_Constants.CUSTOMER_UUID: data.customerUUID,
                Tour_Integration_Constants.PURPOSE: purpose
            }
        else:
            error = {Tour_Integration_Constants.RESPONSE_CODE: 400,
                     Tour_Integration_Constants.RESPONSE_MESSAGE: _error}
        return param, error

    @staticmethod
    def validate_platform_response(response_Code):
        _isValid = False
        _error = {}

        if response_Code == 200:
            _isValid = True
        elif response_Code == 404:
            _error[Tour_Integration_Constants.PLATFORM_DATA] = 'Invalid Platform Data'
        elif response_Code == 400:
            _error[Tour_Integration_Constants.PLATFORM_DATA] = 'Invalid Platform Data'
        return _isValid, _error
