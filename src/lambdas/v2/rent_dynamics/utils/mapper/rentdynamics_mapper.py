import datetime
import re


class RentDynamicsMapper:

    @staticmethod
    def setTransaction(data):
        result = []

        for item in data:
            transaction_type = item["transaction_type"].lower()
            transaction_amount = str(item["amount"])
            is_credit = transaction_type == 'credit'

            if transaction_type == "transaction":
                transaction_type = 'Charge'

            if transaction_type == "payment":
                transaction_type = "Payment"
                transaction_amount = '-' + transaction_amount
                item["notes"] = 'Payment: ' + item["notes"]

            transaction_record = {
                "uniqueIdentifier": item["id"],
                "transactionDate": item["post_date"],
                "amount": transaction_amount,
                "transactionType": transaction_type,
                "chargeCode": item["charge_code_id"],
                "note": item["notes"] if item["notes"] is not None else '',
                "description": '',
                "isPaid": item["amount"] if (transaction_type != "payment") or is_credit else None
            }

            trans_date = datetime.datetime.strptime(
                item["post_date"], "%Y-%m-%d %H:%M:%S")
            expire_date = trans_date + datetime.timedelta(days=30)
            transaction_record['description'] = f"{item['charge_code_name']} for {trans_date} to {expire_date}"

            result.append(transaction_record)

        return result

    @staticmethod
    def setChargeCode(data):
        result = []

        for item in data:
            charge_record = {
                "description": item["name"],
                "chargeCode": item["id"]
            }
            result.append(charge_record)

        return result

    @staticmethod
    def setResidentDetails(data):
        result = []
        resident_dict = {}

        for item in data:
            resident_id = item["resident_id"]

            if resident_id not in resident_dict:
                resident_dict[resident_id] = {
                    'residentId': item["resident_id"],
                    'prospectId': item["prospect_id"],
                    'firstName': item["first_name"],
                    'lastName': item["last_name"],
                    'SSN': item["ssn"],
                    'DOB': item["dob"],
                    'emailAddress': item["email"],
                    'phone': item["phone"],
                    'address': item["address"],
                    'apt': item["unit_name"],
                    'unitId': item["unit_id"],
                    'city': item["city"],
                    'state': item["state"],
                    'zip': item["postal"],
                    'leaseStartDate': item["lease_start"],
                    'leaseEndDate': item["lease_expire"],
                    'leaseNumber': item["lease_id"],
                    'moveInDate': item["move_in_date"],
                    'moveOutDate': item["move_out_date"],
                    'customerInfo': item["res_type"],
                    'isLeasee': True
                }

        result.extend(list(resident_dict.values()))
        return result

    @staticmethod
    def setCustomerEventDetails(data):
        result = []
        TextNumberRegex = "([a-zA-Z]+)([0-9]+)"
        for item in data:
            # Extract the event ID using the regular expression
            match = re.search(TextNumberRegex, item["id"])
            if match:
                event_id = match.group(2)
            else:
                event_id = ""

            event_record = {
                "eventType": item["type"],
                "eventDate": item["date"],
                "internalPMSystemID": event_id,
                "agentID": "",
                "adSource": "",
                "created": item["created_at"],
                "eventDetails": '',
                "personID": item["persons.id"]
            }
            result.append(event_record)

        return result

    @staticmethod
    def setUnitDetails(data):
        result = []
        unit_dict = {}

        for item in data:
            floor_plan_id = item["unit_type_id"]
            unit_price = item["rent_amount"]
            unit_occupancy_status = item["occupancy_status"]
            unit_lease_status = item["lease_status"]
            unit_name = item["unit_name"]
            unit_is_active = item["is_active"]

            if floor_plan_id not in unit_dict:
                description = str(item["bedrooms"]) + \
                    " Bed, " + str(item["bathrooms"]) + " Bath"
                average_sqft = int(item["square_feet"])
                unit_dict[floor_plan_id] = {
                    'floorPlanId': floor_plan_id,
                    'description': description,
                    'averageSquareFeet': average_sqft,
                    'bedrooms': item["bedrooms"],
                    'bathrooms': item["bathrooms"],
                    'marketRent': unit_price,
                    'unitCount': 0,
                    'units': [],
                    'unitsAvailable': 0,
                    'isFloorPlanActive': True
                }

            unit_details = {
                'unitId': item["id"],
                'marketRent': unit_price,
                'occupancyStatus': unit_occupancy_status,
                'leaseStatus': unit_lease_status,
                'unitNumber': unit_name,
                'isActive': unit_is_active,
                'exclude': False,
                'rentReady': unit_lease_status in ['On Notice', 'Available']
            }

            if unit_lease_status in ['Vacant - Not Leased', 'NTV - Available']:
                unit_dict[floor_plan_id]['unitsAvailable'] += 1

            unit_dict[floor_plan_id]['unitCount'] += 1

            if item["unit_type_id"] == 0:
                unit_details['exclude'] = True
                unit_details['isActive'] = False

            unit_dict[floor_plan_id]['units'].append(unit_details)

            if unit_dict[floor_plan_id]['unitCount'] == 0:
                unit_dict[floor_plan_id]['isFloorPlanActive'] = False

        result.extend(list(unit_dict.values()))
        return result

    @staticmethod
    def setPropertyDetails(data):
        result = []
        for item in data:
            # here we have to replace 'communityUUID' string with actual community UUID
            _data = {'propertyId': item["id"],
                     'name': item["name"],
                     'address': item["address"],
                     'city': item["city"],
                     'state': item["state"],
                     'zip': item["postal"],
                     'phoneNumber': item["phone"]
                     }

            result.append(_data)
        return result

    @staticmethod
    def set_prospect_details(data):
        result_dict = {}
        for prospect in data:
            if prospect['prospect_id'] not in result_dict:
                result_dict[prospect['prospect_id']] = {
                        'prospectId': prospect['prospect_id'],
                        'firstName': prospect['first_name'],
                        'middleName': "",
                        'lastName': prospect['last_name'],
                        'emailAddress': prospect['email'],
                        'phone': prospect['phone'],
                        'address': prospect['address'],
                        'city': prospect['city'],
                        'state': prospect['state'],
                        'zip': prospect['postal'],
                        'targetMoveInDate': prospect['desired_move_date'],
                        'desiredBedrooms': prospect['desired_bedrooms'],
                        'desiredNumberOccupants': prospect['additional_occupants'],
                        'petInfo': prospect['pets']
                    }
        return list(result_dict.values())

