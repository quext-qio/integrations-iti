import logging 

from DataPushPullShared.Utilities.DataController import DataValidation, Schema, date_filter
from DataPushPullShared.Utilities.Convert import Convert
from ExceptionHandling.Model.Exceptions import ValidationError
from ExceptionHandling.Utilities.ErrorCode import ErrorCode
from VendorShared.Model.ServiceRequest import ServiceRequest
from VendorShared.Utilities.VendorConstants import VendorConstants
from ResidentShared.Model.ResidentResponse import Resident as qResident
from DataPushPullShared.Utilities.Entities import Resident, Person
from DataPushPullShared.Utilities.DataController import QuextIntegrationConstants
from sqlalchemy import and_
from sqlalchemy_paginator import Paginator

class ResidentController:
    """
    ResidentController handles the resident related business operations by
    communicating with necessary services based on the request given.
    """

    def __validate(self, servicerequest: ServiceRequest):
        """
        Perform the basic validation on the request input for performing operations on the residents

        Parameters
        ----------
        service_request : ServiceRequest
            The input request
        """
        _isValid, _errors = DataValidation.schema(Schema.PLATFORM_DATA, servicerequest.payload)
        if _errors:
            raise ValidationError(ErrorCode.ERROR_DATA_0001, _errors)

    def get_residents(self, servicerequest: ServiceRequest):
        """
        Call the IPS service and resolve the vendor based the IPS response

        Parameters
        ----------
        service_request : ServiceRequest
            The input request
        """
        # validating input request
        resident_response = []
        self.__validate(servicerequest = servicerequest)                 
        session = servicerequest.outgoing.sql.get(VendorConstants.MDM_DB).session()
        Query = session.query(Person).join(
            Resident, Person.person_id == Resident.person_id
        ).filter(
            and_(Person.customer_id==(servicerequest.payload[VendorConstants.CUSTOMER_UUID]),
            Person.community_id==(servicerequest.payload[VendorConstants.COMMUNITY_UUID]))
        )
        Query = date_filter(Person, Query, servicerequest)
        paginator = Paginator(Query, QuextIntegrationConstants.DEFAULT_LIMIT)
        paginate_response = {
            QuextIntegrationConstants.TOTAL_PAGES: paginator.total_pages,
            QuextIntegrationConstants.CURRENT_PAGE: servicerequest.page
        }
        if servicerequest.page < 1 or servicerequest.page > paginator.total_pages:
            return resident_response, paginate_response
        page = paginator.page(servicerequest.page)
        session.close()
        Validator = Convert()
        for row in page.object_list:
            resident = qResident(row.community_id,row.external_id, row.first_name, row.last_name, row.email_address, row.mobile_phone)        
            resident.createdAt = Validator.dateValidator(row.created_date)
            resident.updatedAt = Validator.dateValidator(row.updated_date)
            resident.personId = row.person_id 
            resident_response.append(resident)
        return resident_response, paginate_response

