import json
import requests
from datetime import datetime, timedelta
from abstract.service_interface import ServiceInterface
from utils.service_response import ServiceResponse
from utils.mapper.bedroom_mapping import bedroom_mapping
from configuration.realpage.realpage_config import ilm_config
from services.shared.quext_tour_service import QuextTourService


class RealPageILMService(ServiceInterface):
    # ----------------------------------------------------------------------------------------------
    # Get data from RealPage ILM endpoint
    def get_data(self, body: dict, ips_response: dict, logger):
        logger.info(f"Getting data from RealPage ILM")
        # Tour schedule process
        prospect_comments = body["guestComment"] if "guestComment" in body else ""
        format_date = ""
        hour = ""
        appointment_date = ""
        available_times = []
        tour_scheduled_id = None
        tour_error = ""

        if "tourScheduleData" in body:
            appointment_date = body["tourScheduleData"]["start"]
            if appointment_date != "":
                converted_date = datetime.strptime(appointment_date.replace(
                    "T", " ")[0:appointment_date.index("Z")].strip(), '%Y-%m-%d %H:%M:%S')
                format_date = converted_date.strftime("%B %d, %Y")
                hour = converted_date.strftime("%I:%M:%S %p")
                code, quext_response = QuextTourService.save_quext_tour(body)
                if code != 200:
                    tour_error = quext_response["error"]["message"]
                    headers = {
                        'Access-Control-Allow-Origin': '*',
                        'Content-Type': 'application/json',
                    }
                    available_times = QuextTourService.get_available_times(
                        body["platformData"], body["tourScheduleData"]["start"], "Quext", headers)
                else:
                    tour_scheduled_id = quext_response["data"]["id"]
                    tour_comment = f' --TOURS--Tour Scheduled for {format_date} at {hour}'
                    prospect_comments = prospect_comments + tour_comment

        # Get values of [realpage_property, realpage_id] depend of RealPage Type
        realpage_property = "Lead2Lease Property Id" if "l2l" in ips_response[
            "purpose"]["guestCards"]["partner_system"].lower() else "ILM Property Id"
        realpage_id = ips_response["params"]["property_id"]

        # Create headers for RealPage L2L
        _headers = {
            'Content-Type': 'application/json',
            'apikey': ilm_config[f"{body['source']}_realpage_l2l_apikey"],
            "x-model-version": ips_response["params"]["x-model-version"],
        }

        # Update headers for RealPage ILM
        if "ilm" in ips_response["purpose"]["guestCards"]["partner_system"].lower():
            _headers.update(
                {"x-routing-key": ips_response["params"]["x-routing-key"]})
            _headers.update(
                {"apikey": ilm_config[f"{body['source']}_realpage_ilm_apikey"], })

        # Create body for RealPage ILM
        body_realpage_ilm = json.dumps(
            self._create_body_realpage_ilm(
                body,
                realpage_property,
                realpage_id,
                prospect_comments,
                appointment_date,
                hour,
            )
        )

        errors = {}
        try:
            # call RealPage ILM endpoint
            response_ilm = requests.post(
                f"{ilm_config['ilm_host']}", headers=_headers, data=body_realpage_ilm)
            data = json.loads(response_ilm.content.decode('utf-8-sig'))

            # Case: RealPage ILM returned error code (Bad Request)
            if response_ilm.status_code < 200 or response_ilm.status_code > 299:
                errors = {
                    "message": f"RealPage ILM returned error code {response_ilm.status_code} with message {data['Message']}"
                    }
                logger.error(errors)
                return {
                    'statusCode': "400",
                    'body': json.dumps({
                        'data': {},
                        'errors': errors
                    }),
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    'isBase64Encoded': False
                }

            # Case: RealPage ILM returned success code (OK)
            tour_information = {
                "availableTimes": available_times,
                "tourScheduledID": tour_scheduled_id,
                "tourRequested": appointment_date,
                "tourSchedule": True if tour_scheduled_id else False,
                "tourError": tour_error
            }

            # Format response of RealPage ILM
            serviceResponse = ServiceResponse(
                guest_card_id=data["ConfirmationId"],
                first_name=body["guest"]["first_name"],
                last_name=body["guest"]["last_name"],
                tour_information=tour_information,
            ).format_response()

            return {
                'statusCode': "200",
                'body': json.dumps({
                    'data': serviceResponse,
                    'errors': {}
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'isBase64Encoded': False
            }

        # Case: Unhandled error in RealPage ILM (Internal Server Error)
        except Exception as e:
            logger.error(f"Unhandled Error in RealPage ILM: {e}")
            errors = {
                "message": str(e)
            }
            return {
                'statusCode': "500",
                'body': json.dumps({
                    'data': {},
                    'errors': errors
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'isBase64Encoded': False
            }

    # ----------------------------------------------------------------------------------------------
    # Creates a body of RealPage ILM endpoint
    def _create_body_realpage_ilm(
        self,
        body: dict,
        realpage_property: str,
        realpage_id: str,
        prospect_comments: str,
        appointment_date: str,
        hour: str,
    ) -> dict:
        guest = body["guest"]
        guestPreference = body["guestPreference"]

        # Get values of bedroooms
        bedroooms_data = []
        if "desiredBeds" in guestPreference:
            # Map string to int using [bedroom_mapping]
            for i in range(len(guestPreference["desiredBeds"])):
                string_beds = guestPreference["desiredBeds"][i]
                bedroooms_data.append(bedroom_mapping.get(string_beds, 0))

        # Create new body
        new_body = {
            "Prospects": [
                {
                    "TransactionData": {
                        "Identification": [
                            {
                                "IDType": realpage_property,
                                "IDValue": realpage_id
                            },
                            {
                                "IDType": "GoogleID",
                                "IDValue": "Quext"
                            }
                        ]
                    },
                    "Customers": [
                        {
                            "Name": {
                                "FirstName": guest["first_name"],
                                "LastName": guest["last_name"]
                            },
                            "Phone": [
                                {
                                    "PhoneType": "cell",
                                    "PhoneNumber": guest["phone"] if "phone" in guest else ""
                                }
                            ],
                            "Email": guest["email"] if "email" in guest else "",
                        }
                    ],
                    "CustomerPreferences": {
                        "TargetMoveInDate": guestPreference["moveInDate"],
                        "DesiredRent": {
                            "Max": guestPreference["desiredRent"] if "desiredRent" in guestPreference else 0
                        },
                        "DesiredNumBedrooms": {
                            "Min": min(bedroooms_data) if len(bedroooms_data) > 0 else 0,
                            "Max": max(bedroooms_data) if len(bedroooms_data) > 0 else 0
                        },
                        "Comment": prospect_comments
                    },

                }
            ]
        }

        #  Validate if [Date] in body
        if appointment_date != "":
            converted_hour = datetime.strptime(hour, "%I:%M:%S %p")
            one_hour = converted_hour + timedelta(hours=1)
            end_hour = one_hour.strftime("%I:%M:%S")
            end_date = appointment_date[:appointment_date.index("T")]
            new_body["Prospects"][0].update(
                {
                    "Events": [
                        {
                            "EventType": "virtualTour",
                            "ScheduledActivity": {
                                "ActivityType": "appointment",
                                "ActivityDuration": {
                                    "StartDate": f'{appointment_date[ : appointment_date.index("Z")]}-05:00',
                                    "EndDate": f'{end_date}T{end_hour}-05:00'
                                }
                            }
                        }
                    ]
                }
            )

        return new_body
