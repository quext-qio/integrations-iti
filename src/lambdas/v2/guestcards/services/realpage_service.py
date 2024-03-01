import json
import re
from abstract.service_interface import ServiceInterface
from constants.realpage_constants import RealpageConstants
from utils.service_response import ServiceResponse
from datetime import datetime
import dateutil.parser
import os
import suds
import requests
import xml.etree.ElementTree as ET
from IPSController import IpsV2Controller
from services.shared.realpage_times import DataRealpage

from env_reader import EnvReader

env_instance = EnvReader.get_instance().get_ips_envs()


class RealPageService(ServiceInterface):
    def get_data(self, body: dict, ips_response: dict, logger):
        logger.info(f"Getting data from RealPage")
        code, partners = IpsV2Controller().get_list_partners(
            body["platformData"]["communityUUID"])
        partners = partners.json()
        customer = body["guest"]
        preferences = body["guestPreference"]
        today_date = datetime.now().strftime("%Y-%m-%d")
        tour_information = None
        ips_partner_response = partners
        partner_uuid = ips_partner_response[0]['partner']['partnerId'] if (ips_partner_response and
                                                                           len(ips_partner_response) > 0 and
                                                                           ips_partner_response[0]) else ""

        api_creds = ""
        outgoingIPSSecurityResponse = ""
        pmcid = ""
        siteid = ""
        licensekey = ""
        client = None
        if partner_uuid:
            headers = {
                'Content-Type': 'application/json',
                'apikey': env_instance['api_key'],
                'x-ips-consumer-id': env_instance['consumer_id']
            }
            outgoingIPSSecurityResponse = requests.get(
                f'{env_instance["ips_host"]}/api/v2/partner/partner-security/security-v1/{partner_uuid}', headers=headers)
            security_response = outgoingIPSSecurityResponse.json()

            # CREATING CLIENT CONNECTION WITH API CREDENTIALS RETURNED FROM SECURITY RESPONSE
            if isinstance(security_response, dict) and security_response and security_response.get(RealpageConstants.PARTNER_NAME) == RealpageConstants.REALPAGE:
                    # getting api credentials
                    api_creds = security_response[RealpageConstants.SECURITY][RealpageConstants.CREDENTIALS][0][RealpageConstants.BODY][RealpageConstants.DH]
                    imp = suds.xsd.doctor.Import(RealpageConstants.IMPORT_HOST, location=RealpageConstants.IMPORT_LOCATION)
                    imp.filter.add(RealpageConstants.XML_SOAP)
                    doctor = suds.xsd.doctor.ImportDoctor(imp)
                    # creating client connection
                    client = suds.Client(
                        api_creds[RealpageConstants.WSDL], doctor=doctor)
                    c = api_creds[RealpageConstants.WSDL]
                    pmcid = api_creds[RealpageConstants.PMCID]
                    siteid = api_creds[RealpageConstants.SITEID]
                    licensekey = api_creds[RealpageConstants.LICENSE_KEY]
        if not client:
            # creating client connection
            client = suds.client.Client(RealpageConstants.DHWSDL)

        factory = client.factory
    # Preparing auth details from service request
        _auth = client.factory.create('AuthDTO')
        _auth.pmcid = ips_response["params"]["foreign_customer_id"] if "foreign_customer_id" in ips_response["params"] else pmcid
        _auth.siteid = ips_response["params"]["foreign_community_id"] if "foreign_community_id" in ips_response["params"] else siteid
        _auth.licensekey = licensekey

        # Assuming you have a generated class for PhoneNumber
        _phone_number = factory.create('PhoneNumber')
        cleaned_phone_number = ''.join(filter(str.isdigit, customer["phone"]))
        if len(cleaned_phone_number) == 10:
            cleaned_phone_number = "1" + cleaned_phone_number

        _phone_number.type = "Mobile"
        _phone_number.number = self.clean_and_validate_phone_number(
            "+"+cleaned_phone_number)

        # Assuming you have a generated class for ArrayOfPhoneNumber
        array_of_phone_number = factory.create('ArrayOfPhoneNumber')
        array_of_phone_number.PhoneNumber.append(_phone_number)

        # Getting prospect details from payload
        _prospect = factory.create('Prospect')
        _prospect.firstname = customer["first_name"]
        _prospect.lastname = customer["last_name"]
        _prospect.email = customer["email"]
        _prospect.relationshipid = "H"
        _prospect.numbers = factory.create('Numbers')
        _prospect.numbers.phonenumbers = array_of_phone_number

        _arrayofprospect = factory.create('ArrayOfProspect')
        _arrayofprospect.Prospect.append(_prospect)

        _preferences = factory.create('Preferences')
        _preferences.dateneeded = today_date
        _preferences.occupants = str(preferences["noOfOccupants"])
        _preferences.desiredrent = str(preferences["desiredRent"])
        _preferences.leasetermmonths = str(preferences["leaseTermMonths"])

        appointment_data = None
        _guestcard = client.factory.create('GuestCard')
        _guestcard.datecontact = today_date
        _guestcard.datefollowup = today_date
        _guestcard.prospects = _arrayofprospect
        _guestcard.createdate = today_date
        _guestcard.statusisactive = True
        _guestcard.statusisleased = False
        _guestcard.statusislost = False
        _guestcard.moveinreason = preferences.get("moveInReason", "")
        _guestcard.skipduplicatecheck = False
        _guestcard.daysbackduplicatecheck = 91
        _guestcard.prospectcomment = body["guestComment"]
        _guestcard.preferences = _preferences

        if body.get("tourScheduleData") and body["tourScheduleData"].get("start"):
            appointment_date = body["tourScheduleData"].get("start")
            converted_date = datetime.strptime(appointment_date.replace(
                "T", " ")[0:appointment_date.index("Z")].strip(), '%Y-%m-%d %H:%M:%S')
            date_str = dateutil.parser.parse(appointment_date)
            format_date = converted_date.strftime("%B %d, %Y")
            hour = converted_date.strftime("%I:%M:%S %p")
            tour_comment = f' --TOURS--Tour Scheduled for {format_date} at {hour}'
            appointment_data = factory.create('Appointment')
            appointment_data.day = str(date_str.day)
            appointment_data.hour = str(date_str.hour)
            appointment_data.minute = str(date_str.minute)
            appointment_data.month = str(date_str.month)
            appointment_data.year = str(date_str.year)
            appointment_data.tasknotes = tour_comment

        _guestcard.appointment = appointment_data

        try:
            res = client.service.insertprospect(
                auth=_auth, guestcard=_guestcard)

            customer_id = res["InsertProspectResponse"]["Guestcard"]["ID"]
            if appointment_data and customer_id:
                tour_information = {
                    "availableTimes": [],
                    "tourScheduledID": customer_id,
                    "tourRequested": appointment_date,
                    "tourSchedule": True if customer_id else False,
                    "tourError": ""
                }
            if res["InsertProspectResponse"]["Guestcard"]["Status"] != "Success":
                if appointment_data:
                    payload = {
                            "timeData": {
                                "fromDate": appointment_date,
                                "toDate": appointment_date
                            },
                            "platformData": body["platformData"]
                    }
                    tour_information = {
                        "availableTimes": DataRealpage().get_tour_availability(partners, payload, ips_response),
                        "tourScheduledID": customer_id,
                        "tourRequested": appointment_date,
                        "tourSchedule": True if customer_id else False,
                        "tourError": ""
                    }

            serviceResponse = ServiceResponse(
                guest_card_id=customer_id,
                first_name=body["guest"]["first_name"],
                last_name=body["guest"]["last_name"],
                status=res["InsertProspectResponse"]["Guestcard"]["Status"],
                action=res["InsertProspectResponse"]["Guestcard"]["Action"],
                message=res["InsertProspectResponse"]["message"],
                tour_information=tour_information,
            ).format_response()

            return {
                'statusCode': "200",
                'body': json.dumps({
                    'data': serviceResponse,
                    'errors': []
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'isBase64Encoded': False
            }

        except Exception as e:
            logger.error(
                {"Error trying to insert guestcard to Realpage": f"{e}"})
            return {
                'statusCode': "500",
                'body': json.dumps({
                    'data': [],
                    'errors': [{"message": f"{e}"}]
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'isBase64Encoded': False
            }

    def clean_and_validate_phone_number(self, number):
        """
        Cleans and validates US phone number using regular expression.
        Returns cleaned phone number if valid, otherwise returns None.
        """
        # Regular expression pattern for US phone numbers
        pattern = re.compile(
            r'^(\+1)?[\s-]?\(?(\d{3})\)?[\s-]?(\d{3})[\s-]?(\d{4})$')
        # Check if the number matches the pattern
        match = pattern.match(number)
        if not match:
            return None
        # Extract and format the phone number components
        country_code = match.group(1)
        area_code = match.group(2)
        prefix = match.group(3)
        suffix = match.group(4)
        # Clean the phone number by removing country code and non-digit characters
        phone_number = f"{country_code} {area_code}-{prefix}-{suffix}"
        # Return the cleaned phone number
        return phone_number
