import json
import re
import types
from datetime import datetime, timedelta

from pytz import timezone


class Utils:

    # Bedrooms mapping
    bedroom_mapping = {
        "ONE_BEDROOM": 1,
        "TWO_BEDROOM": 2,
        "THREE_BEDROOM": 3,
    }

    @staticmethod
    def merge_object_to_pydantic_object(obj_1, obj_2):
        """
            Merges attributes from a dictionary or SimpleNamespace object into a Pydantic object,
            appending new attributes not already defined in the Pydantic object.

            Args:
                obj_1 (Any): The Pydantic object to merge into.
                obj_2 (Union[dict, SimpleNamespace]): The data source (dictionary or SimpleNamespace).

            Returns:
                Any: The updated Pydantic object.

            Raises:
                TypeError: If the data source is neither a dictionary nor a SimpleNamespace.
            """

        for attr, value in obj_2.__dict__.items():
            setattr(obj_1, attr, value)

        return obj_1

    @staticmethod
    def json_to_object(json_obj):
        """
        Convert JSON object to Python object.

        Args:
            json_obj (dict or list or any): JSON object to convert.

        Returns:
            any: Converted Python object.
        """
        if isinstance(json_obj, dict):
            obj = types.SimpleNamespace(**{k: Utils.json_to_object(v) for k, v in json_obj.items()})
        elif isinstance(json_obj, list):
            obj = [Utils.json_to_object(x) for x in json_obj]
        else:
            obj = json_obj
        return obj

    @staticmethod
    def convert_appointment_date(date_time):
        """
        Convert appointment date from one format to another.

        Args:
            date_time (str): Date and time string to convert.

        Returns:
            tuple: Converted date string and datetime object.
        """
        converted_date = datetime.strptime(date_time.replace(
            "T", " ")[0:date_time.index("Z")].strip(), '%Y-%m-%d %H:%M:%S')
        return converted_date.strftime("%B %d, %Y"), converted_date

    @staticmethod
    def convert_datetime_timezone(dt, from_timezone, to_timezone, from_format, to_format):
        """
        Convert datetime format and timezone.

        Args:
            dt (str): Datetime string to convert.
            from_timezone (str): Source timezone.
            to_timezone (str): Target timezone.
            from_format (str): Source datetime format.
            to_format (str): Target datetime format.

        Returns:
            str: Converted datetime string.
        """
        dt = timezone(from_timezone).localize(
            datetime.strptime(re.sub('[a-zA-Z]', '', dt), from_format))
        dt = dt.astimezone(timezone(to_timezone))
        dt = dt.strftime(to_format)
        return dt

    @staticmethod
    def generate_time_slots(input_list):
        """
        Generate availability time slots based on input list of dictionaries.

        Args:
            input_list (list): List of dictionaries containing start and end times.

        Returns:
            list: List of sorted time slots.
        """
        final_result = []

        for i in range(len(input_list)):
            start, end = input_list[i].values()
            res = []
            start_time = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
            sth, stm = start_time.hour, start_time.minute
            end_time = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')
            end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
            eth, etm = end_time.hour, end_time.minute
            if abs(sth - eth) in (0, 1) and abs(stm - etm) in (15, 45):
                continue
            maximum = max(sth, eth)
            if sth == maximum:
                res.append(start_time_str)
                while sth >= eth:
                    if sth == eth and (stm - etm) <= 15:
                        break
                    final_time = start_time - timedelta(minutes=30)
                    final_time_str = final_time.strftime('%Y-%m-%d %H:%M:%S')
                    res.append(final_time_str)
                    start_time = final_time
                    sth, stm = final_time.hour, final_time.minute
            elif eth == maximum:
                res.append(end_time_str)
                while eth >= sth:
                    if sth == eth and (etm - stm) <= 15:
                        break
                    final_time = end_time - timedelta(minutes=30)
                    final_time_str = final_time.strftime('%Y-%m-%d %H:%M:%S')
                    res.append(final_time_str)
                    end_time = final_time
                    eth, etm = final_time.hour, final_time.minute
            final_result += res
        return sorted(list(set(final_result)))

    def construct_guest_card_response(self, response):
        """
        Construct guest card response.

        Args:
            response: Data to be used for constructing the response.

        Returns:
            dict: Constructed response.
        """
        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': {
                    "guestCardInformation": {
                        "guestCardId": response.guest_card_id,
                        "message": response.message,
                        "firstName": response.first_name,
                        "lastName": response.last_name,
                        "result": response.result,
                        "status": response.status,
                        "action": response.action,
                    },
                    "tourInformation": response.tour_information
                },
                'errors': {}
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'isBase64Encoded': False
        }

