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
import xmltodict

class RealPageService(ServiceInterface):
    def get_data(self, body: dict, ips_response: dict):      
            # Get Partner Info
            outgoingIPSPartnerChannelResponse = ips_response
            customer =  body["guest"]
            tour_information = None
            ips_partner_response = outgoingIPSPartnerChannelResponse
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
                    if len(security_response['content']) > 0:
                        for i in security_response['content']:
                            if i['partner_name'] == "RealPage":
                                client = suds.client.Client(api_creds[RealpageConstants.WSDL])  # creating client connection
                                pmcid = api_creds[RealpageConstants.PMCID]
                                siteid = api_creds[RealpageConstants.SITEID]
                                licensekey = api_creds[RealpageConstants.LICENSE_KEY]
                                break

            if not client:
                client = suds.client.Client(RealpageConstants.DHWSDL)  # creating client connection

            factory = client.factory
        # Preparing auth details from service request
            _auth = client.factory.create('AuthDTO')
            _auth.pmcid = pmcid
            _auth.siteid = siteid
            _auth.licensekey = licensekey

               
            _phone_number = factory.PhoneNumber(type="Home",number=customer["phone"])            
            array_of_phone_number = factory.ArrayOfPhoneNumber(_phone_number)
                                                        
                        # Getting prospect details from payload
            _prospect = factory.Prospect(
                                        firstname= customer["first_name"],
                                        lastname= customer["last_name"],
                                        email= customer["email"],
                                        relationshipid="H",
                                        numbers=factory.Numbers(phonenumbers=array_of_phone_number))

            _arrayofprospect = factory.ArrayOfProspect(_prospect)
            _preferences =  _preferences = factory.Preferences(dateneeded=datetime.date.today(),occupants = "3",desiredrent="1200", leasetermmonths = "12") 
            appointment_data = None                          

            if body.get("tourScheduleData") and body["tourScheduleData"].get("start"):
                    
                    appointment_date = body["tourScheduleData"].get("start")
                    converted_date = datetime.strptime(appointment_date.replace("T", " ")[0:appointment_date.index("Z")].strip(), '%Y-%m-%d %H:%M:%S')
                    date_str = dateutil.parser.parse(appointment_date)
                    format_date = converted_date.strftime("%B %d, %Y")
                    hour = converted_date.strftime("%I:%M:%S %p")
                    tour_comment = f' --TOURS--Tour Scheduled for {format_date} at {hour}'
                    appointment_data = factory.Appointment(day=date_str.day,hour=date_str.hour,minute=date_str.minute,month=date_str.month,year=date_str.year,tasknotes=tour_comment)  
                             

            _guestcard = factory.GuestCard(
                                    datecontact = datetime.date.today(), 
                                    datefollowup = datetime.date.today(),
                                    prospects = _arrayofprospect, 
                                    createdate = datetime.date.today(),
                                    statusisactive = True, 
                                    statusisleased = False, 
                                    statusislost = False,
                                    skipduplicatecheck = False, 
                                    daysbackduplicatecheck = 91,
                                    prospectcomment = "HOLA",
                                    preferences = _preferences,
                                    appointment = appointment_data
                                    ) 
            
            try:
                res = client.service.insertprospect(auth=_auth, guestcard = _guestcard)
                response = xmltodict.parse(ET.tostring(res))
                # Parse the JSON response
                response_data = json.loads(json.dumps(response))

                # Extract the ID value
                customer_id = response_data["InsertProspectResponse"]["Guestcard"]["ID"]
                                         
                serviceResponse = ServiceResponse(
                        guest_card_id= customer_id,
                        first_name=body["guest"]["first_name"],
                        last_name=body["guest"]["last_name"],
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

    
        