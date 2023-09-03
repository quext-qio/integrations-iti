import json
from abstract.service_interface import ServiceInterface
from constants.realpage_constants import RealpageConstants
from utils.service_response import ServiceResponse
import logging
from datetime import datetime
import dateutil.parser
import os
import suds
import requests
import xml.etree.ElementTree as ET
from IPSController import IPSController
from services.shared.realpage_times import DataRealpage

class RealPageService(ServiceInterface):
    def get_data(self, body: dict, ips_response: dict):     
            code, partners =  IPSController().get_list_partners(body["platformData"]["communityUUID"])
            partners = json.loads(partners.text)
            customer =  body["guest"]
            preferences = body["guestPreference"]
            today_date = datetime.now().strftime("%Y-%m-%d")
            tour_information = None
            ips_partner_response = partners
            partner_uuid = ips_partner_response['content'][0]['uuid'] if ips_partner_response.get('content', "") and len(
                ips_partner_response.get('content')) > 0 else ""
         
            api_creds = ""
            outgoingIPSSecurityResponse = ""
            pmcid = ""
            siteid = ""
            licensekey = ""
            client = None
            if partner_uuid:  
                    host = os.environ['ACL_HOST']
                    outgoingIPSSecurityResponse = requests.get(f'{host}/api/partners/security/{partner_uuid}?redacted=off')
                    security_response = json.loads(outgoingIPSSecurityResponse.text)

                    #CREATING CLIENT CONNECTION WITH API CREDENTIALS RETURNED FROM SECURITY RESPONSE
                    if len(security_response[RealpageConstants.CONTENT]) > 0:
                        for i in security_response[RealpageConstants.CONTENT]:
                            if i[RealpageConstants.PARTNER_NAME] == RealpageConstants.REALPAGE:
                                api_creds = i[RealpageConstants.SECURITY][RealpageConstants.CREDENTIALS][0][RealpageConstants.BODY][RealpageConstants.DH] # getting api credentials
                                imp = suds.xsd.doctor.Import(RealpageConstants.IMPORT_HOST, location=RealpageConstants.IMPORT_LOCATION)
                                imp.filter.add(RealpageConstants.XML_SOAP)
                                doctor = suds.xsd.doctor.ImportDoctor(imp)
                                client = suds.Client(api_creds[RealpageConstants.WSDL], doctor=doctor)  # creating client connection
                                pmcid = api_creds[RealpageConstants.PMCID]
                                siteid = api_creds[RealpageConstants.SITEID]
                                licensekey = api_creds[RealpageConstants.LICENSE_KEY]

            if not client:
                client = suds.client.Client(RealpageConstants.DHWSDL)  # creating client connection

            factory = client.factory
        # Preparing auth details from service request
            _auth = client.factory.create('AuthDTO')
            _auth.pmcid = pmcid if pmcid != "" else ips_response["platformData"]["foreign_customer_id"]
            _auth.siteid = siteid if siteid != "" else ips_response["platformData"]["foreign_community_id"]
            _auth.licensekey = licensekey if licensekey != "" else "b5020fd1-d0ff-4559-973f-84bc7cc8e210"

            # Assuming you have a generated class for PhoneNumber
            _phone_number = factory.create('PhoneNumber')
            _phone_number.type = "Home"
            _phone_number.number = customer["phone"]

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
            _guestcard.moveinreason = preferences["moveInReason"]
            _guestcard.skipduplicatecheck = False
            _guestcard.daysbackduplicatecheck = 91
            _guestcard.prospectcomment = body["guestComment"]
            _guestcard.preferences = _preferences                    

            if body.get("tourScheduleData") and body["tourScheduleData"].get("start"):
                    appointment_date = body["tourScheduleData"].get("start")
                    converted_date = datetime.strptime(appointment_date.replace("T", " ")[0:appointment_date.index("Z")].strip(), '%Y-%m-%d %H:%M:%S')
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
                res = client.service.insertprospect(auth=_auth, guestcard = _guestcard)
              
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
                                    {
                                        "timeData": {
                                            "fromDate": appointment_date,
                                            "toDate": appointment_date
                                        },
                                        "platformData": body["platformData"]
                                    }
                                }
                        tour_information = {
                            "availableTimes": DataRealpage.get_tour_availability(partners,payload,ips_response),
                            "tourScheduledID": customer_id,
                            "tourRequested": appointment_date,
                            "tourSchedule": True if customer_id else False,
                            "tourError": ""
                        }
                        
                serviceResponse = ServiceResponse(
                        guest_card_id= customer_id,
                        first_name=body["guest"]["first_name"],
                        last_name=body["guest"]["last_name"],
                        status=res["InsertProspectResponse"]["Guestcard"]["Status"],
                        action=res["InsertProspectResponse"]["Guestcard"]["Action"],
                        message=res["InsertProspectResponse"]["message"],
                        tour_information=tour_information,
                    ).format_response()
                

                return  {
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

    
        