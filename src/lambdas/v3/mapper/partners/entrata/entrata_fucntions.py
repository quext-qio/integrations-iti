import json
import os
from datetime import datetime

from pytz import timezone

from AwsHelper.ssm_helper import GetParameterValue
from qoops_logger import Logger
from src.lambdas.v3.constants.entrata_v3_constants import EntrataV3Constants
from src.lambdas.v3.constants.v3_constants import V3Constants, MethodConstants
from src.lambdas.v3.utils.utils import Utils

logger = Logger().instance('Entrata functions')
parameter = GetParameterValue()


def process_pre_conditions(func):
    def wrapper(self, request_data):
        # Set process_request flag to True indicating pre-processing is done
        request_data.process_request = True

        # Set created_date attribute to current time in MST timezone
        request_data.created_date = datetime.now(timezone('MST')).strftime(EntrataV3Constants.ENTRATA_DATE)

        # Determine contact types and lead communication method
        request_data.contact_types = request_data.customer_preference.preferred_communication if hasattr(
            request_data.customer_preference, "preferred_communication") else []
        request_data.lead_communication = 'email' in request_data.contact_types and '1' or '0'

        # Determine contact points and opt-in phone
        request_data.contact_points = 'email' in request_data.contact_types and '1' or '0'
        request_data.opt_in_phone = 'phone' in request_data.contact_types and '1' or '0'

        # Set personal_number attribute to cell_phone, home_phone, or office_phone
        request_data.personal_number = request_data.cell_phone or request_data.home_phone or request_data.office_phone

        # Construct event data
        request_data.event = {
            "event": [
                {
                    "typeId": EntrataV3Constants.GUESTCARD_ID,
                    "type": EntrataV3Constants.GUESTCARD_METHOD,
                    "date": request_data.created_date,
                    "eventReason": request_data.customer_preference.move_in_reason if hasattr(
                        request_data.customer_preference, 'move_in_reason') else ""
                }
            ]
        }

        # Call the original function with updated request_data
        result = func(self, request_data)
        return result

    return wrapper


def post_process_time_availability_data(func):
    def wrapper(self, request_data, response):
        # Convert response to JSON format
        response = json.loads(response.text)

        # Extract availability data from the response
        response = (response[EntrataV3Constants.RESPONSE][EntrataV3Constants.RESULT][
            EntrataV3Constants.PROPERTY_CALENDAR_AVAILABILITY])

        # Process available time slots
        for value in response[EntrataV3Constants.AVAILABLE_HOURS][EntrataV3Constants.AVAILABLE_HOUR]:
            start_time = value[EntrataV3Constants.DATE] + ' ' + value[EntrataV3Constants.START_TIME]
            end_time = value[EntrataV3Constants.DATE] + ' ' + value[EntrataV3Constants.END_TIME]

            # Convert time zones
            start_time = Utils.convert_datetime_timezone(start_time, EntrataV3Constants.ENTRATA_TIMEZONE,
                                                         EntrataV3Constants.QUEXT_TIMEZONE,
                                                         EntrataV3Constants.DATETIME_FORMAT,
                                                         '%Y-%m-%d %H:%M:%S')
            end_time = Utils.convert_datetime_timezone(end_time, EntrataV3Constants.ENTRATA_TIMEZONE,
                                                       EntrataV3Constants.QUEXT_TIMEZONE,
                                                       EntrataV3Constants.DATETIME_FORMAT,
                                                       '%Y-%m-%d %H:%M:%S')
            start_time = start_time.split(' ')
            end_time = end_time.split(' ')
            if start_time[0] and end_time[0]:
                value[EntrataV3Constants.DATE] = start_time[0]
                value[EntrataV3Constants.START_TIME] = start_time[1]
                value[EntrataV3Constants.END_TIME] = end_time[1]

        # Call the original function with updated request_data and response
        result = func(self, request_data, response)
        return result

    return wrapper


class EntrataFunctions:
    """
    Class containing methods for handling Entrata-related functionalities.
    """

    def pre_process_entrata_request_data_for_time_availability(self, request_data):
        """
        Pre-processes Entrata request data for time availability.

        Args:
            request_data: The request data to be processed.

        Returns:
            Processed request data.
        """
        request_data.process_request = False
        request_data.tour_information = None
        if hasattr(request_data, "tour_schedule_data") and hasattr(request_data.tour_schedule_data,
                                                                   "appointment_date"):
            request_data.process_request = True
            request_data.format_date, request_data.converted_date = Utils.convert_appointment_date(
                request_data.tour_schedule_data.appointment_date)
            request_data.hour = f'{request_data.converted_date.hour}:{request_data.converted_date.minute}'
            tour_start = datetime.strptime(request_data.tour_schedule_data.appointment_date, "%Y-%m-%dT%H:%M:%SZ")
            request_data.output_timestamp = tour_start.strftime("%m/%d/%Y")
        return request_data

    @process_pre_conditions
    def pre_process_entrata_request_data_for_guest_card(self, request_data):
        """
        Pre-processes Entrata request data for generating guest card.

        Args:
            request_data: The request data to be processed.

        Returns:
            Processed request data.
        """
        bedroom_data = []
        if hasattr(request_data.customer_preference, "desired_num_of_beds"):
            for i in range(len(request_data.customer_preference.desired_num_of_beds)):
                bedroom_data.append(
                    Utils.bedroom_mapping.get(request_data.customer_preference.desired_num_of_beds[i], 0))
        request_data.bed_rooms = str(max(bedroom_data)) if len(bedroom_data) > 0 else 0
        if hasattr(request_data, 'tour_schedule_data'):
            event_reason_id = request_data.params.eventreason_id if hasattr(request_data, 'params') and hasattr(
                request_data.params, 'eventreason_id') and request_data.params.eventreason_id != 0 else str(
                EntrataV3Constants.EVENT_REASON_ID)
            request_data.event = {
                "event": [
                    {
                        "type": EntrataV3Constants.BOOK_TOUR_EVENT,
                        "date": request_data.created_date,
                        "comments": request_data.tour_comment,
                        "eventReasonId": event_reason_id
                    }
                ]
            }
        return request_data

    @post_process_time_availability_data
    def post_process_entrata_response_data_for_time_availability(self, request_data, response):
        """
        Post-processes Entrata response data for time availability.

        Args:
            request_data: The request data used for processing.
            response: The response data from Entrata.

        Returns:
            Tuple containing processed request data and response.
        """
        # Generate available time slots
        time_slot, request_data.available_times = [], []
        for items in response[EntrataV3Constants.AVAILABLE_HOURS][EntrataV3Constants.AVAILABLE_HOUR]:
            start_time = items[EntrataV3Constants.DATE] + 'T' + items[EntrataV3Constants.START_TIME]
            end_time = items[EntrataV3Constants.DATE] + 'T' + items[EntrataV3Constants.END_TIME]
            time_slot.append(
                {EntrataV3Constants.START_TIME: start_time, EntrataV3Constants.END_TIME: end_time})
            request_data.available_times = Utils.generate_time_slots(time_slot)

        # Update request data with available time slots information
        request_data.tour_error = ""
        request_data.tour_comment = None
        request_data.tour_schedule = False
        if request_data.tour_schedule_data.appointment_date.replace("T", " ")[
           0:request_data.tour_schedule_data.appointment_date.index("Z")] not in request_data.available_times:
            request_data.tour_requested = request_data.tour_schedule_data.appointment_date
            request_data.tour_error = "Not created. No time slots available for that start time"
        else:
            request_data.times = []
            request_data.tour_requested = request_data.tour_schedule_data.appointment_date
            request_data.tour_schedule = True
            request_data.tour_comment = "Tour Scheduled for " + request_data.format_date + " at " + request_data.hour
        return request_data, response

    def post_process_entrata_response_data_for_guest_card(self, request_data, response):
        """
        Post-processes Entrata response data for guest card generation.

        Args:
            request_data: The request data used for processing.
            response: The response data from Entrata.

        Returns:
            Tuple containing processed request data and response.
        """
        request_data.guest_card_id = str(response[EntrataV3Constants.APPLICANT_ID])
        tour_schedule_id = response[EntrataV3Constants.APPLICANT_ID] if request_data.tour_schedule else ""
        if request_data.tour_requested != "":
            request_data.tour_information = {
                "availableTimes": request_data.available_times,
                "tourScheduledID": tour_schedule_id,
                "tourRequested": request_data.tour_requested,
                "tourSchedule": True if tour_schedule_id else False,
                "tourError": request_data.tour_error
            }
        request_data.status = "NEW"
        request_data.result = "SUCCESS"
        request_data.action = "INSERT"
        request_data.message = None
        return request_data, response

    def validate_time_availability(self, request_data, response):
        """
        Validates time availability based on the response from Entrata.

        Args:
            request_data: The request data used for processing.
            response: The response data from Entrata.

        Returns:
            Tuple containing processed request data and response.
        """
        request_data.valid_response = True
        if response.status_code != 200:
            request_data.valid_response = False
            # Identify the error and raise it accordingly
            if V3Constants.ERROR in response[V3Constants.RESPONSE]:
                logger.info("Got no records for Tour Availability from Entrata")
                request_data.valid_response = False
                return {V3Constants.MESSAGE: response[V3Constants.RESPONSE][V3Constants.ERROR][
                    V3Constants.MESSAGE]}
        return request_data, response

    def validate_guest_card_response(self, request_data, response):
        """
        Validates the response from Entrata for guest card generation.

        Args:
            request_data: The request data used for processing.
            response: The response data from Entrata.

        Returns:
            Tuple containing processed request data and response.
        """
        request_data.valid_response = True
        response = json.loads(response.text)
        response_body = response[EntrataV3Constants.RESPONSE][EntrataV3Constants.RESULT][EntrataV3Constants.PROSPECTS][
            EntrataV3Constants.PROSPECT][
            0] if EntrataV3Constants.RESULT in response[EntrataV3Constants.RESPONSE] else response[
            EntrataV3Constants.RESPONSE]

        if EntrataV3Constants.ERROR in response[EntrataV3Constants.RESPONSE] or (
                EntrataV3Constants.CODE in response[EntrataV3Constants.RESPONSE] and
                response[EntrataV3Constants.RESPONSE][EntrataV3Constants.CODE] != 200):
            error = response[EntrataV3Constants.RESPONSE][EntrataV3Constants.ERROR][
                EntrataV3Constants.MESSAGE] if EntrataV3Constants.ERROR in response[
                EntrataV3Constants.RESPONSE] else response_body[EntrataV3Constants.MESSAGE]
            request_data.valid_response = False
            return {
                'statusCode': response[EntrataV3Constants.RESPONSE][
                    EntrataV3Constants.CODE] if EntrataV3Constants.CODE in response[
                    EntrataV3Constants.RESPONSE] else 500,
                'body': json.dumps({
                    'data': [],
                    'errors': [{EntrataV3Constants.MESSAGE: error}]
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'isBase64Encoded': False
            }
        response = response_body
        return request_data, response

    def get_params(self, request_data):
        """
        Retrieves parameters for the Entrata API request.

        Args:
            request_data: The request data used for processing.

        Returns:
            Updated request data with request parameters.
        """
        purpose_params = {
            "properties": {
                MethodConstants.METHOD: MethodConstants.GET_CALENDAR_AVAILABILITY
            },
            "leads": {
                MethodConstants.METHOD: MethodConstants.ONLINE_GUEST_CARD
            }
        }

        request_data.request_params = purpose_params[request_data.partner_endpoint_name] if (
                request_data.partner_endpoint_name in purpose_params) else None

        return request_data

    def get_headers(self, headers_data):
        """
        Retrieves headers for the Entrata API request.

        Args:
            headers_data: The existing headers data.

        Returns:
            Updated headers data with Entrata API key.
        """
        headers_data.update({'Authorization': f'Basic {os.environ.get("ENTRATA_APIKEY")}'})
        return headers_data
