import json
import logging
from datetime import datetime

from CalendarServiceShared.Utilities.CalendarConstants import CalendarConstants
from ExceptionHandling.Model.Exceptions import GatewayError, ValidationError
from ExceptionHandling.Utilities.ErrorCode import ErrorCode, ErrorConstants
from PostLeadManagementShared.Constants.Contants import HTTP_SERVER_ERROR_MSJ
from TourShared.Model.Data_Model import Data
from TourShared.Model.Data_Model import TourAvailabilityData
from Utils.Headers import Headers
from VendorShared.Model.ServiceRequest import ServiceRequest
from VendorShared.Utilities.VendorConstants import VendorConstants, get_source_and_agent
from DataPushPullShared.Utilities.Convert import Convert


class CalendarGatewayController:
    """
    CalendarGatewayController class for handling Quext Calendar related communication and data transformations
    """

    def post_appointment(self, service_request: ServiceRequest):
        """
        Create Appointment with Quext Calendar

        Params:
        -------
        service_request: ServiceRequest - ServiceRequest Object which contains request parameters

        Return:
        -------
        dict: Response of Save tour scheduling
        """
        start_date = service_request.request.payload[VendorConstants.TOUR_SCHEDULE_DATA][VendorConstants.START]
        prospect = service_request.request.payload.get(VendorConstants.PROSPECT) and \
                   service_request.request.payload[VendorConstants.PROSPECT] or {}
        customer_preference = service_request.request.payload.get(VendorConstants.CUSTOMER_PREFERENCE) or None
        move_in_date = customer_preference.get(VendorConstants.MOVE_IN_DATE) \
                       and customer_preference[VendorConstants.MOVE_IN_DATE] or None
        desired_rent = customer_preference.get(VendorConstants.DESIRED_RENT) \
                       and customer_preference[VendorConstants.DESIRED_RENT] or 0
        comments = service_request.guest_card_comment

        source, agent_id = get_source_and_agent(service_request.auth.get_property('source'), service_request)
        phone_number = prospect.get(VendorConstants.PHONE) and prospect[VendorConstants.PHONE] or ''

        request = {
            "appointmentData": {
                "firstName": prospect[VendorConstants.FIRSTNAME],
                "lastName": prospect[VendorConstants.LASTNAME],
                "email": prospect[VendorConstants.EMAIL] or '',
                "phone": phone_number,
                "layout": customer_preference.get(VendorConstants.DESIRED_BEDROOM) \
                          and customer_preference[VendorConstants.DESIRED_BEDROOM],
                "priceCeiling": int(desired_rent),
                "moveInDate": move_in_date,
                "notes": comments,
                "start": start_date,
                "source": source
            },
            "platformData": {
                "communityUUID": service_request.payload[VendorConstants.COMMUNITY_UUID],
                "customerUUID": service_request.payload[VendorConstants.CUSTOMER_UUID]
            }
        }
        logging.info("Request Payload for Quext Calendar : {}".format(request))
        outgoing_channel = service_request.outgoing.plain_http[CalendarConstants.QUEXT_SCHEDULE_TOUR]
        code, quext_response = CalendarGateway().post_calendar(outgoing_channel.conn, service_request.cid, request)
        logging.info("Quext Calendar Response code : {}".format(code))
        logging.debug("{}".format(quext_response))

        # If errors
        if code != 200:
            logging.info("Error in saving Quext calender")
            availabletimes = self.get_available_times(service_request, start_date)
            availabletimes.update(quext_response)
            logging.info(availabletimes)
            return availabletimes
        else:
            tour_scheduled_id = quext_response[CalendarConstants.DATA][CalendarConstants.APPOINTMENT_ID]
            logging.info("Tour scheduled in Quext calendar - AppointmentID: {}".format(tour_scheduled_id))
            converted_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ')
            format_date = converted_date.strftime("%B %d, %Y")
            hour = f'{converted_date.hour}:{converted_date.minute}'
            quext_response[CalendarConstants.DATA][CalendarConstants.COMMENTS] = \
                " --TOURS--Tour Scheduled for " + format_date + " at " + hour
            logging.info(quext_response)
        return quext_response

    def get_tour_availability(self, service_request: ServiceRequest, tour_availability_data: TourAvailabilityData):

        """
        Fetch Availability date from Quext Calendar Service
        """

        outgoing_platform_request = service_request.outgoing.plain_http[
            VendorConstants.GET_CALENDAR_AVAILABILITY_OUTGOING_CHANNEL]
        payload = {i: j for i, j in service_request.request.payload.items()}
        payload = {
            "timeData": vars(tour_availability_data),
            "platformData": {
                "communityUUID": service_request.payload['communityUUID'],
                "customerUUID": service_request.payload['customerUUID']
            }
        }
        response = CalendarGateway().get_availability(conn=outgoing_platform_request.conn, cid=service_request.cid,
                                                      params=payload)
        response_list = [i for i in response[CalendarConstants.AVAILABLE_TIMES]]
        return Data(**{"availableTimes": response_list})

    def get_available_times(self, service_request: ServiceRequest, date):
        """
        Call quext get available times
        """
        date = date[0:date.index('T')]
        request = {
            "timeData": {
                "fromDate": date,
                "toDate": date
            },
            "platformData": {
                "customerUUID": service_request.payload[VendorConstants.CUSTOMER_UUID],
                "communityUUID": service_request.payload[VendorConstants.COMMUNITY_UUID]
            }
        }
        logging.info("get_available_time body: {}".format(request))
        outgoing_channel = service_request.outgoing.plain_http[CalendarConstants.QUEXT_GET_AVAILABILITY]

        response = CalendarGateway().get_availability(conn=outgoing_channel.conn, cid=service_request.cid,
                                                      params=request)
        
        logging.info("Quext availability response : {}".format(response))
        response_list = [i for i in response[CalendarConstants.AVAILABLE_TIMES]]
        utc_date_list = Convert.get_utc(response_list, 'UTC')
        return {"availableTimes": utc_date_list}


class CalendarGateway:
    """
    ResManGateway to connect ResMan service to exchange the data
    """

    def post_calendar(self, conn, cid, body):
        """
        Implements All ResMan API Endpoint and returns the response

        Parameters
        ----------
        conn : Outgoing Connection Object
        body : Api request data
        cid : Zato Connection ID

        Returns
        --------
        dict
        """
        headers = Headers(methods='OPTIONS, HEAD, POST')
        headers.add(key='Accept', value='application/json')
        try:
            response = conn.post(cid, json.dumps(body), headers=headers.get())
            response_body = json.loads(response.text)
            logging.info("Quext Calender Response : {}".format(response_body))

            # If errors
            if response.status_code < 200 or response.status_code >= 300:
                data = {
                    "data": {},
                    "error": {
                        "message": response_body["message"]
                    },
                }
                return response.status_code, data

            # Success case
            data = {
                "data": {
                    "appointment_id": response_body["appointment_id"]
                },
                "error": {},
            }
            return 200, data
        except Exception as e:
            logging.error(f"Error Quext Calendar: {e}")
            data = {
                "data": {},
                "error": HTTP_SERVER_ERROR_MSJ,
            }
            return 500, data

    def get_availability(self, conn, cid, params):
        """
        Implements Calendar API Endpoint from Quext Calendar and returns the response

        Parameters
        ----------
        conn : Outgoing Connection Object
        params : Api Query Parameters
        headers : Api Headers
        cid : Zato Connection ID

        Returns
        --------
        dict
        """
        try:
            # Connecting ResMan
            response = conn.post(cid, params)
        except Exception as e:
            logging.exception(e.__str__())
            raise GatewayError(ErrorCode.ERROR_HTTP_0001, ErrorConstants.INVALID_DATA, VendorConstants.BAD_REQUEST)
        # Preparing response object
        response_content = response.json()
        # Checking the status of the response
        if response.status_code != 201:
            logging.debug("Invalid Response : {}".format(response))
            if 'json' in dir(response):
                error_resp = response.json()
            else:
                error_resp = ErrorConstants.INVALID_DATA
            raise GatewayError(ErrorCode.ERROR_HTTP_0001, error_resp, response.status_code)
        return response_content
