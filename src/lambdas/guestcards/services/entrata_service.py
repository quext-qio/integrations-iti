import json, logging, requests, uuid, re
from datetime import datetime, timedelta
from pytz import timezone
from constants.entrata_constants import EntrataConstants
from abstract.service_interface import ServiceInterface
from utils.service_response import ServiceResponse
from configuration.entrata.entrata_config import config as entrata_config
from utils.mapper.bedroom_mapping import bedroom_mapping

class EntrataService(ServiceInterface):
    def get_data(self, body: dict, ips_response: dict):
            logging.info("GuestCard: Entrata")

            headers = {
            "Content-Type": "application/json",
            "Authorization": f'Basic {entrata_config[EntrataConstants.APIKEY]}' 
            }
            _headers = headers
            tour_comment = None
            tour_requested = ""
            tour_error = ""
            tour_schedule = False
            tour_information = None
            times = []
            tour = body[EntrataConstants.TOUR_DATA] if EntrataConstants.TOUR_DATA in body else {}
            if tour:
                    appointment_date = body[EntrataConstants.TOUR_DATA]["start"]
                    if appointment_date != "":
                      
                        converted_date = datetime.strptime(appointment_date.replace("T", " ")[0:appointment_date.index("Z")].strip(), '%Y-%m-%d %H:%M:%S')
                        format_date = converted_date.strftime("%B %d, %Y")
                        hour = f'{converted_date.hour}:{converted_date.minute}'
                        times , tour_errors= self.get_entrata_available_times(ips_response, body[EntrataConstants.TOUR_DATA])
                        available_times = times["availableTimes"] if "availableTimes" in times else []
                        if appointment_date.replace("T", " ")[0:appointment_date.index("Z")] not in available_times:
                            tour_requested = appointment_date
                            tour_error = "Not created. No time slots available for that start time"
                        else:
                            times = []
                            tour_requested = appointment_date
                            tour_schedule = True
                            tour_comment = "Tour Scheduled for " + format_date + " at " + hour
                        
                    
            data = self.__get_from_payload_for_guestcards(body, ips_response, tour, tour_comment)
            request_body = {
                            "auth": {
                                "type": "basic"
                            },
                            "requestId": str(uuid.uuid1()),
                            "method": {
                                "name": str(EntrataConstants.SENDLEADS),
                                "version": "r1",
                                "params": data
                        }
                    }

            _params = self.__get_parameters(EntrataConstants.GUESTCARD_METHOD)

            outgoing_entrata = f'{entrata_config[EntrataConstants.HOST]}/api/leads'
            response = requests.post(outgoing_entrata, data=json.dumps(request_body), params=_params, headers=_headers)
            # Checking for Empty list
            response = json.loads(response.text)
            response_body = response[EntrataConstants.RESPONSE][EntrataConstants.RESULT][EntrataConstants.PROSPECTS][EntrataConstants.PROSPECT][0] if EntrataConstants.RESULT in response[EntrataConstants.RESPONSE] else response[EntrataConstants.RESPONSE]
            
            if EntrataConstants.ERROR in response[EntrataConstants.RESPONSE] or (EntrataConstants.CODE in response[EntrataConstants.RESPONSE] and  response[EntrataConstants.RESPONSE][EntrataConstants.CODE] != 200):
                error = response[EntrataConstants.RESPONSE][EntrataConstants.ERROR][EntrataConstants.MESSAGE] if EntrataConstants.ERROR in response[EntrataConstants.RESPONSE] else response_body[EntrataConstants.MESSAGE]
                return {
                            'statusCode': response[EntrataConstants.RESPONSE][EntrataConstants.CODE] if EntrataConstants.CODE in response[EntrataConstants.RESPONSE] else 500,
                            'body': json.dumps({
                                'data': [],
                                'errors': [{EntrataConstants.MESSAGE: error}]
                            }),
                            'headers': {
                                'Content-Type': 'application/json',
                                'Access-Control-Allow-Origin': '*',  
                            },
                            'isBase64Encoded': False  
                        }
            
            tour_schedule_id = response_body[EntrataConstants.APPLICANT_ID] if tour_schedule else ""
            if tour_requested != "":
                tour_information = {
                    "availableTimes": times,
                    "tourScheduledID": tour_schedule_id,
                    "tourRequested": tour_requested,
                    "tourSchedule": True if tour_schedule_id else False,
                    "tourError": tour_error
                }
            serviceResponse = ServiceResponse(
                    guest_card_id= response_body[EntrataConstants.APPLICANT_ID],
                    first_name=body[EntrataConstants.GUEST][EntrataConstants.FIRST_NAME],
                    last_name=body[EntrataConstants.GUEST][EntrataConstants.LAST_NAME],
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
            
                    
        
   
    def __get_from_payload_for_guestcards(self, payload, ips, tour_info, tour_comment = None):

        prospect = payload[EntrataConstants.GUEST]

        customer_preference = payload[EntrataConstants.GUEST_PREFERENCE]
        bedroooms_data = []
        contact_types = customer_preference.get("contactPreference", [])
        if EntrataConstants.DESIRED_BEDS in customer_preference:
                # Map string to int using [bedroom_mapping]
                for i in range(len(customer_preference[EntrataConstants.DESIRED_BEDS])):
                    string_beds = customer_preference[EntrataConstants.DESIRED_BEDS][i]
                    bedroooms_data.append(bedroom_mapping.get(string_beds, 0))
        bedrooms = str(max(bedroooms_data)) if len(bedroooms_data) > 0 else 0

        desired_bathroom = customer_preference.get(EntrataConstants.DESIRED_BATHS,0) # Default value if not specified in the payload
        desired_rent = customer_preference.get(EntrataConstants.DESIRED_RENT, 0)
        occupants = customer_preference.get(EntrataConstants.NO_OCCUPANTS, 0)
        lease_term_months = customer_preference.get(EntrataConstants.LEASE_TERMS, 0)
        preferred_amenities = customer_preference.get(EntrataConstants.PREFERRED_AMENITIES, "")
        
        move_in_date = datetime.strptime(payload[EntrataConstants.GUEST_PREFERENCE][EntrataConstants.MOVE_IN_DATE], "%Y-%m-%dT%H:%M:%SZ")
        move_date = move_in_date.strftime(EntrataConstants.ENTRATA_DATE)

        now_date = datetime.now(timezone('MST')).strftime(EntrataConstants.ENTRATA_DATE)
        event_reason_id = ips["platformData"][EntrataConstants.EVENTREASON_ID] if EntrataConstants.EVENTREASON_ID in ips["platformData"] and ips["platformData"][EntrataConstants.EVENTREASON_ID] != 0 else str(EntrataConstants.EVENT_REASON_ID)

        event = {
            "event": [
                {
                    "typeId": EntrataConstants.GUESTCARD_ID,
                    "type": EntrataConstants.GUESTCARD_METHOD,
                    "date": now_date,
                    "eventReason": customer_preference.get(EntrataConstants.MOVEIN_REASON, "")
                }
            ]
        }

        if tour_info:
            event = {
                "event": [
                    {
                        "type": EntrataConstants.BOOK_TOUR_EVENT,
                        "date": now_date,
                        "comments": tour_comment,
                        "eventReasonId": event_reason_id
                    }
                ]
            }

        param_dict = {
            "propertyId": ips["platformData"]["foreign_community_id"],
            EntrataConstants.PROSPECTS: {
                EntrataConstants.PROSPECT: {
                    "leadSource": {
                        "originatingLeadSourceId": ips["platformData"][EntrataConstants.LEADSOURCE_ID]
                    },
                    "createdDate": now_date,
                    "customers": {
                        "customer": {
                            "name": {
                                "firstName": prospect[EntrataConstants.FIRST_NAME],
                                "lastName": prospect[EntrataConstants.LAST_NAME]
                            },
                            "phone": {
                                "personalPhoneNumber": prospect[EntrataConstants.PHONE]
                            },
                            "email": prospect[EntrataConstants.EMAIL] or '',
                            "marketingPreferences": {
                                "email": {
                                    "optInLeadCommunication": EntrataConstants.EMAIL in contact_types and "1" or "0",
                                    "optInMessageCenter": "0",
                                    "optInContactPoints": EntrataConstants.EMAIL in contact_types and "1" or "0",
                                    "optInMarketingMessages": "0"
                                },
                                "optInphone": EntrataConstants.PHONE in contact_types and "1" or "0",
                                "optInMail": "0"
                            }
                        }
                    },
                    "customerPreferences": {
                        "desiredMoveInDate": move_date,
                        EntrataConstants.DESIRED_RENT: {
                            "min": desired_rent,
                            "max": desired_rent
                        },
                        "desiredNumBedrooms": str(bedrooms),
                        "desiredNumBathrooms": desired_bathroom,
                        "desiredLeaseTerms": lease_term_months,
                        "numberOfOccupants": occupants,
                        "comment": payload.get("guestComment", "")
                    },
                    "events": event
                }
            }
        }
        
        return param_dict
    

    def get_entrata_available_times(self, ips, date_tour):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Basic {entrata_config[EntrataConstants.APIKEY]}' 
            }
        _headers = headers
        tour_start = datetime.strptime(date_tour["start"], "%Y-%m-%dT%H:%M:%SZ")
        output_timestamp = tour_start.strftime("%m/%d/%Y")
        # Getting parameter from payload
        _body = {
            EntrataConstants.PROPERTYID: ips["platformData"]["foreign_community_id"],
            EntrataConstants.FROM_DATE: output_timestamp,
            EntrataConstants.TO_DATE: output_timestamp
            }
        request_body = {
                "auth": {
                    "type": "basic"
                },
                "requestId": str(uuid.uuid1()),
                "method": {
                    "name": str(EntrataConstants.GET_CALENDAR_AVAILABILITY),
                    "version": "r1",
                    "params": _body
            }
        }

        _params = {
            "method": str(EntrataConstants.GET_CALENDAR_AVAILABILITY)
        }

        outgoing_entrata = f'{entrata_config[EntrataConstants.HOST]}/api/properties'
        response = requests.post(outgoing_entrata, data=json.dumps(request_body), params=_params, headers=_headers)
        # Checking for Empty list
        response = json.loads(response.text)
        if EntrataConstants.ERROR in response[EntrataConstants.RESPONSE]:
            logging.info("Got no records for Tour Availability from Entrata")
            return [], {EntrataConstants.MESSAGE: response[EntrataConstants.RESPONSE][EntrataConstants.ERROR][EntrataConstants.MESSAGE] }
        res = (response[EntrataConstants.RESPONSE][EntrataConstants.RESULT][
                EntrataConstants.PROPERTY_CALENDAR_AVAILABILITY])
        for value in res[EntrataConstants.AVAILABLE_HOURS][EntrataConstants.AVAILABLE_HOUR]:
            start_time = value[EntrataConstants.DATE]+' '+value[EntrataConstants.START_TIME]
            end_time = value[EntrataConstants.DATE]+' '+value[EntrataConstants.END_TIME]
            
            start_time = convert_datetime_timezone(start_time, EntrataConstants.ENTRATA_TIMEZONE,
                                                            EntrataConstants.QUEXT_TIMEZONE,  
                                                            EntrataConstants.DATETIME_FORMAT, 
                                                            '%Y-%m-%d %H:%M:%S')
            end_time = convert_datetime_timezone(end_time, EntrataConstants.ENTRATA_TIMEZONE, 
                                                            EntrataConstants.QUEXT_TIMEZONE, 
                                                            EntrataConstants.DATETIME_FORMAT, 
                                                            '%Y-%m-%d %H:%M:%S')
            start_time = start_time.split(' ')
            end_time = end_time.split(' ')
            if start_time[0] and end_time[0]:
                value[EntrataConstants.DATE] = start_time[0]
                value[EntrataConstants.START_TIME] = start_time[1]
                value[EntrataConstants.END_TIME] = end_time[1]
        time_slot = []
        for items in res[EntrataConstants.AVAILABLE_HOURS][EntrataConstants.AVAILABLE_HOUR]:
            starttime = items[EntrataConstants.DATE] + 'T'+ items[EntrataConstants.START_TIME]
            endtime = items[EntrataConstants.DATE] + 'T' + items[EntrataConstants.END_TIME]
            time_slot.append({EntrataConstants.START_TIME: starttime, EntrataConstants.END_TIME: endtime })
            availableTimes = generate_time_slots(time_slot)

        return {"availableTimes": availableTimes}, {}
    
    def __get_parameters(self, method: str = ""):
        """
        Returns the URL parameters 

        Parameters
        ----------
        method : URL Method (properties , customers , etc)
        """
        params = {
                   "method": str(method)
            }

        return params
    
def convert_datetime_timezone(dt, from_timezone, to_timezone, from_format, to_format):
    """
    Convert datetime format and timezone
    """
    dt = timezone(from_timezone).localize(datetime.strptime(re.sub('[a-zA-Z]','', dt), from_format))
    dt = dt.astimezone(timezone(to_timezone))
    dt = dt.strftime(to_format)
    return dt

def generate_time_slots(input_list):
        '''
        Method to tour availability time slots based on input list of dict
        '''
        final_result = []

        for i in range(len(input_list)):
            start, end = input_list[i].values()
            res = []
            start_time = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
            sth,stm = start_time.hour,start_time.minute
            end_time = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')
            end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
            eth,etm = end_time.hour, end_time.minute
            if (abs(sth-eth) in (0,1) and abs(stm-etm) in (15,45)) :
                continue;
            maximum = max(sth,eth)
            if sth == maximum:
                res.append(start_time_str)
                while sth >= eth:
                    if (sth==eth and (stm-etm)<=15) :
                        break;
                    final_time = start_time - timedelta(minutes = 30)
                    final_time_str = final_time.strftime('%Y-%m-%d %H:%M:%S')
                    res.append(final_time_str)
                    start_time = final_time
                    sth,stm = final_time.hour, final_time.minute
            elif eth == maximum:
                res.append(end_time_str)
                while eth >= sth:
                    if (sth==eth and (etm-stm)<=15) :
                        break;
                    final_time = end_time - timedelta(minutes = 30)
                    final_time_str = final_time.strftime('%Y-%m-%d %H:%M:%S')
                    res.append(final_time_str)
                    end_time = final_time
                    eth,etm = final_time.hour, final_time.minute
            final_result += res
        return sorted(list(set(final_result)))






         