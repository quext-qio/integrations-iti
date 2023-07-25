class IdentityErrorHandler:
    _validation_messages = {
        "FirstName": "FirstName can only contain letters, single quote, dash, and space characters.",
        "LastName": "LastName can only contain letters, single quote, dash, and space characters.",
        "MiddleName": "MiddleName can only contain letters, single quote, dash, and space characters.",
        "Suffix": "Suffix can only contain letters and numbers.",
        "BirthDate": "Birthdate should be in MMDDYYYY format.",
        "Ssn": "SSN can only contain numbers.",
        "Phone": "Phone can only contain numbers.",
        "EmailAddress": "Must be a valid email address format such as quext@integrations.com.",
        "StreetAddress": "StreetAddress can only contain letters, numbers, and space characters.",
        "City": "City can only contain letters, single quote, dash, and space characters.",
        "State": "State can only contain letters.",
        "PostalCode": "PostalCode can only contain numbers.",
        "IdentificationNumber": "IdentificationNumber can only contain letters and numbers. "
    }

    def __init__(self, errors):
        self.updated_response = errors.copy()

    # updates the validator error messages related to regex for the TransUnion Identity Verify
    def update_error_messages(self):
        # look for errors related to the Applicant fields
        for applicant_items in self.updated_response["Applicant"]:
            for applicant_field_name, applicant_field_value in applicant_items.items():
                if isinstance(applicant_field_value, list):
                    # extra logic needed for the Addresses nested fields
                    if applicant_field_name == "Addresses":
                        for addresses_items in applicant_field_value[0][0]:
                            for addresses_field_name, addresses_field_value in addresses_items.items():
                                if isinstance(addresses_field_value, list):
                                    for temp_index, temp_error in enumerate(addresses_field_value):
                                        if "value does not match regex" in temp_error:
                                            addresses_items[addresses_field_name][temp_index] = self._validation_messages.get(addresses_field_name)
                                else:
                                    if "value does not match regex" in addresses_field_value:
                                        addresses_items[addresses_field_name] = self._validation_messages.get(addresses_field_name)
                    else:
                        for index, error in enumerate(applicant_field_value):
                            if "value does not match regex" in error:
                                applicant_items[applicant_field_name][index] = self._validation_messages.get(applicant_field_name)
                else:
                    if "value does not match regex" in applicant_field_value:
                        applicant_items[applicant_field_name] = self._validation_messages.get(applicant_field_name)
            
            return self.updated_response

