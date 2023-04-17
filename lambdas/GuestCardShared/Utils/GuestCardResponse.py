from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

from VendorShared.Utilities.VendorConstants import VendorConstants
from Utils import CustomLogger

logging = CustomLogger.logger

class GuestCardInformation(BaseModel):
    guestCardId: Optional[int] = Field(None, alias="id")
    message: Optional[str] = Field(None, alias="message")
    firstName: str = None
    lastName: str = None
    result: Optional[str] = Field(None, alias="Result")
    status: Optional[str] = Field(None, alias="Status")
    action: Optional[str] = Field(None, alias="Action")


class TourInformation(BaseModel):
    availableTimes: List = []
    tourScheduledID: Optional[int] = ""
    tourRequested: str = None
    tourSchedule: bool = None
    tourError: Optional[dict] = ""


class GuestCardResponse(BaseModel):
    guestCardInformation: GuestCardInformation = None
    tourInformation: TourInformation = None  

def generate_comments(service_request):
    """
    This method is used to generate comments
    """
    logging.info("Generating comments")

    prospect = service_request.request.payload.get(VendorConstants.PROSPECT) \
                        and service_request.request.payload[VendorConstants.PROSPECT] or None
                        
    comment = 'Message:\n {}'.format(service_request.request.payload.get(VendorConstants.COMMENT)
                        and service_request.request.payload[VendorConstants.COMMENT] or None)
    
    if comment[-1] != "." :
            comment += "."

    phone_number = '{}'.format(prospect.get(VendorConstants.PHONE) \
                                                and prospect[VendorConstants.PHONE] or None)
    phone_number = phone_number.strip()
    if len(phone_number) != 10 or not phone_number.isdigit():
        return "Invalid phone number"
    phone = 'Phone: +1 ({}) {}-{};\n'.format(phone_number[:3], phone_number[3:6], phone_number[6:])

    email = 'Email: {};\n'.format(prospect.get(VendorConstants.EMAIL) and prospect[VendorConstants.EMAIL] \
                                        or None)
    generated_comment = phone + email + comment

    if service_request.request.payload.get(VendorConstants.CUSTOMER_PREFERENCE):

        customerpreference = service_request.request.payload.get(VendorConstants.CUSTOMER_PREFERENCE)

        desired_bedroom = customerpreference.get(VendorConstants.DESIRED_BEDROOM) \
                                                    and customerpreference[VendorConstants.DESIRED_BEDROOM] or []

        beds = convert_bedroom_name(*desired_bedroom)
        formatted_beds = ", ".join(beds)
        desired_rent = customerpreference[VendorConstants.DESIRED_RENT] \
                                if customerpreference.get(VendorConstants.DESIRED_RENT) else None

        phone = 'Phone: +1 ({}) {}-{}; '.format(phone_number[:3], phone_number[3:6], phone_number[6:])
        sms_authorized = "SMS: Authorized;\n" if "sms" in customerpreference[VendorConstants.CONTACT_PREFERENCE] else None

        generated_comment = phone + sms_authorized + email + comment if sms_authorized is not None else phone + email + comment

        move_in_date = customerpreference.get(VendorConstants.MOVE_IN_DATE) \
                            and customerpreference[VendorConstants.MOVE_IN_DATE] or datetime.now().strftime("%Y-%m-%d")
        
        date_obj = datetime.strptime(move_in_date, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d %B %Y')
        comms = service_request.request.payload.get(VendorConstants.COMMENT)

        if comms[-1] != "." :
            comms += "."
            
        preference = 'Prefs:\n\t Beds: {};\n\t Rent Min: ${}; Rent Max: ${};\n\t Needed Date: {};\n\t Comms: {}\n'.format(formatted_beds, desired_rent, desired_rent, formatted_date, comms )

        generated_comment = preference + generated_comment

        logging.info("Generated Comment:\n{}".format(generated_comment))

    if service_request.request.payload.get(VendorConstants.TOUR_SCHEDULE_DATA):
        start = datetime.strptime(service_request.request.payload[VendorConstants.TOUR_SCHEDULE_DATA][VendorConstants.START],"%Y-%m-%dT%H:%M:%SZ")
        formatted_dt = start.strftime("%-d %B %Y @ %-I:%M %p")
        tour_date = 'Tour: {};\n'.format(formatted_dt)
        generated_comment = tour_date + generated_comment
        logging.info("Generated Comment:\n{}".format(generated_comment))
    
    return generated_comment


def convert_bedroom_name(*bedroom_names):
    formatted_names = []
    for name in bedroom_names:
        if name == 'ONE_BEDROOM':
            formatted_names.append("1 Bedroom")
        elif name == 'TWO_BEDROOM':
            formatted_names.append("2 Bedroom")
        elif name == 'THREE_BEDROOM':
            formatted_names.append("3 Bedroom")
        elif name == 'FOUR_BEDROOM':
            formatted_names.append("4 Bedroom")
        elif name == 'STUDIO':
            formatted_names.append("Studio")
        elif name == 'LOFT':
            formatted_names.append("Loft")
        else:
            formatted_names.append("Invalid bedroom name")
    return formatted_names


def generate_comments_no_linebreak(service_request):
    """
    This method is used to generate comments
    """
    logging.info("Generating comments")

    prospect = service_request.request.payload.get(VendorConstants.PROSPECT) \
                        and service_request.request.payload[VendorConstants.PROSPECT] or None
                        
    comment = 'Message: {}'.format(service_request.request.payload.get(VendorConstants.COMMENT)
                        and service_request.request.payload[VendorConstants.COMMENT] or None)
    
    if comment[-1] != "." :
            comment += "."

    phone_number = '{}'.format(prospect.get(VendorConstants.PHONE) \
                                                and prospect[VendorConstants.PHONE] or None)
    phone_number = phone_number.strip()

    if len(phone_number) != 10 or not phone_number.isdigit():
        return "Invalid phone number"
    phone = 'Phone: +1 ({}) {}-{};'.format(phone_number[:3], phone_number[3:6], phone_number[6:])

    email = 'Email: {};'.format(prospect.get(VendorConstants.EMAIL) and prospect[VendorConstants.EMAIL] \
                                        or None)
    generated_comment = phone + email + comment

    if service_request.request.payload.get(VendorConstants.CUSTOMER_PREFERENCE):

        customerpreference = service_request.request.payload.get(VendorConstants.CUSTOMER_PREFERENCE)

        desired_bedroom = customerpreference.get(VendorConstants.DESIRED_BEDROOM) \
                                                    and customerpreference[VendorConstants.DESIRED_BEDROOM] or []

        beds = convert_bedroom_name(*desired_bedroom)
        formatted_beds = ", ".join(beds)
        desired_rent = customerpreference[VendorConstants.DESIRED_RENT] \
                                if customerpreference.get(VendorConstants.DESIRED_RENT) else None

        phone = 'Phone: +1 ({}) {}-{}; '.format(phone_number[:3], phone_number[3:6], phone_number[6:])
        sms_authorized = "SMS: Authorized;" if "sms" in customerpreference[VendorConstants.CONTACT_PREFERENCE] else None

        generated_comment = phone + sms_authorized + email + comment if sms_authorized is not None else phone + email + comment

        move_in_date = customerpreference.get(VendorConstants.MOVE_IN_DATE) \
                            and customerpreference[VendorConstants.MOVE_IN_DATE] or datetime.now().strftime("%Y-%m-%d")
        
        date_obj = datetime.strptime(move_in_date, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d %B %Y')
        comms = service_request.request.payload.get(VendorConstants.COMMENT)

        if comms[-1] != "." :
            comms += "."
            
        preference = 'Prefs: Beds: {}; Rent Min: ${}; Rent Max: ${}; Needed Date: {}; Comms: {}'.format(formatted_beds, desired_rent, desired_rent, formatted_date, comms )

        generated_comment = preference + generated_comment

        logging.info("Generated Comment: {}".format(generated_comment))

    if service_request.request.payload.get(VendorConstants.TOUR_SCHEDULE_DATA):
        start = datetime.strptime(service_request.request.payload[VendorConstants.TOUR_SCHEDULE_DATA][VendorConstants.START],"%Y-%m-%dT%H:%M:%SZ")
        formatted_dt = start.strftime("%-d %B %Y @ %-I:%M %p")
        tour_date = 'Tour: {};'.format(formatted_dt)
        generated_comment = tour_date + generated_comment
        logging.info("Generated Comment:{}".format(generated_comment))
    
    return generated_comment