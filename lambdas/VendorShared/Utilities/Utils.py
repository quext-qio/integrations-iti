import re
from ExceptionHandling.Model.Exceptions import GatewayError, ValidationError, DataError, DateFormatError
from ExceptionHandling.Utilities.ErrorCode import ErrorCode
from VendorShared.Utilities.VendorConstants import VendorConstants
from datetime import datetime
from operator import itemgetter
import hashlib
import base64

def convert_date(date_from:str = None, date_to:str = None, date:str = None):
    """ Converts Date from One Format to Another Format"""
    try:
        return datetime.strptime(datetime.strptime(date, date_from).strftime(date_to),date_to)                                                                         
    except:   
        raise DateFormatError(ErrorCode.ERROR_DATA_0001, error_msg = VendorConstants.INVALID_DATE_FORMAT, \
                     status_code = VendorConstants.BAD_REQUEST)


def validate_date(date_format:str = None, date:str = None):
    """Return boolean value if match exists"""   
    if(bool(re.match(date_format,date))):
        return True
    else:
        raise DateFormatError(ErrorCode.ERROR_DATA_0001, error_msg = VendorConstants.INVALID_DATE_FORMAT, \
                     status_code = VendorConstants.BAD_REQUEST)


def parse_date(date:str = None, date_format:str = None): 
    """Parse the String date to Python date Object"""           
    return datetime.strptime (date, date_format)              


def string_to_md5hex_convert(data:list, separator="-"):
    """convert string to md5 hex value"""
    str_val = separator.join(data).upper()
    return hashlib.md5(str_val.encode()).hexdigest()

def encrypt_base64(message):
    """
    String into a bytes and use Base64 to encode
    """
    message_bytes = repr(message).encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message

def decrypt_base64(base64_message):
    """
    Base64 string to bytes and use Base64 to decode
    """
    if base64_message:
        base64_bytes = base64_message.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')
        return eval(message)

def delta_of_data(insert_data, existing_result):
    """
    Compare and return difference in objects in MDM table
    """
    update_flag = False
    update_dict = {}
    for key,val in vars(insert_data).items():
        if key != '_sa_instance_state' and val != vars(existing_result)[key]:
            update_dict[key] = val
            update_flag = True
    return update_flag, update_dict

def format_phone(phone):
    # strip non-numeric characters
    phone_num = re.sub(r'\D', '', phone)
    # remove leading 1 (area codes never start with 1)
    phone_num = phone_num.lstrip('1')
    formated_phone = None
    if phone_num:
        formated_phone = '({}) {}-{}'.format(phone_num[0:3], phone_num[3:6], phone_num[6:])
    return formated_phone

def min_start_date(list_obj):
    values = []
    for obj in list_obj:
        if obj:
            values.append(obj.start_date)
    return min(values) if len(values) > 0 else None

def max_end_date(list_obj):
    values = []
    for obj in list_obj:
        if obj:
            tuple_value = obj.end_date, obj.lease_interval_status
            values.append(tuple_value)
    return max(values, key=itemgetter(0)) if len(values) > 0 else None

def lease_status_mapping(lease_status):
        """
        Current - Active
        Notice - Active
        Future - Active
        Pending/Pending Transfer - Queued
        Evicted - Terminated
        past - Archived
        """
        switcher = {
            VendorConstants.CURRENT: VendorConstants.ACTIVE,
            VendorConstants.FUTURE: VendorConstants.ACTIVE,
            VendorConstants.NOTICE: VendorConstants.ACTIVE,
            VendorConstants.PENDING: VendorConstants.QUEUED,
            VendorConstants.PENDINGT: VendorConstants.QUEUED,
            VendorConstants.EVICTED: VendorConstants.TERMINATED,
            VendorConstants.PAST: VendorConstants.ARCHIVED
        }
        lease_status = switcher.get(lease_status, None)
        return lease_status


def trim_utc_date(utc_datetime):
        """
        Trim date from the UTC datatime
        """
        if utc_datetime:
            utc_date = utc_datetime.split("T")[0]
            return utc_date
        return utc_datetime