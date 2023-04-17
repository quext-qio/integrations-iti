import logging

from DataPushPullShared.Utilities.DataController import DataValidation, Schema, \
    QuextIntegrationConstants, date_filter
from DataPushPullShared.Utilities.Convert import Convert
from VendorShared.Model.ServiceRequest import ServiceRequest
from VendorShared.Utilities.VendorConstants import VendorConstants
from ExceptionHandling.Utilities.ErrorCode import ErrorCode
from ExceptionHandling.Model.Exceptions import ValidationError
from LocationShared.Model.LocationResponse import Units, Building, UnitRoom
from DataPushPullShared.Utilities.Entities import Unit, UnitSpace
from sqlalchemy import and_
from sqlalchemy_paginator import Paginator

class LocationController:
    """
        Handles the Generic validation and returns the 
        respective vendors Object(Resman,Realpage)
    """

    def __validate(self,params:dict = None, date:str = None, servicerequest:ServiceRequest = None):
        """         
        Validates the input payload(communityUUId,customerUUId) 
        and returns the Boolean Value

        Parameters
        ----------
        params: Dictionary
        """       
        
        isvalid, _error = DataValidation.schema(Schema.PLATFORM_DATA,params) 
        
        if(_error):
            raise ValidationError(ErrorCode.ERROR_HTTP_0001, _error)

    def get_locations(self,servicerequest:ServiceRequest):        
        """         
        Returns the Locations Endpoint results by resolving the Vendor using the factory design
        pattern and implement the respective third party endpoint. 

        Parameters
        ----------
        servicerequest: Zato Request Object
        """
        location_response = []
        self.__validate(params = servicerequest.payload, servicerequest = servicerequest)
        session = servicerequest.outgoing.sql.get(VendorConstants.MDM_DB).session()

        Query = session.query(Unit, UnitSpace).join(UnitSpace,
                UnitSpace.unit_id == Unit.unit_id, isouter=True).filter(
                and_(Unit.customer_id==(servicerequest.payload[VendorConstants.CUSTOMER_UUID]),
                Unit.community_id==(servicerequest.payload[VendorConstants.COMMUNITY_UUID]))
        )

        Query = date_filter(Unit, Query, servicerequest)
        paginator = Paginator(Query, QuextIntegrationConstants.DEFAULT_LIMIT)
        paginate_response = {
            QuextIntegrationConstants.TOTAL_PAGES: paginator.total_pages,
            QuextIntegrationConstants.CURRENT_PAGE: servicerequest.page
        }
        if servicerequest.page < 1 or servicerequest.page > paginator.total_pages:
            return location_response, paginate_response
        page = paginator.page(servicerequest.page)
        session.close()
        building_ids = []
        unit_ids = []
        Validator = Convert()
        for row in page.object_list:
            external_id = "{}-{}".format(row.Unit.community_id, row.Unit.building)
            if  external_id not in building_ids:
                building_ids.append(external_id)
                location_response.append(Building(communityId=row.Unit.community_id, \
                externalId=external_id, name=row.Unit.unit_name, createdAt=Validator.dateValidator(row.Unit.created_date), \
                updatedAt=Validator.dateValidator(row.Unit.updated_date)))
            if  row.Unit.external_id not in unit_ids:
                unit_ids.append(row.Unit.external_id)
                # Building the Units Response using the Unit Model
                location_response.append(Units(communityId=row.Unit.community_id, \
                externalId=row.Unit.external_id, locationId=row.Unit.unit_id,\
                parentIdExternal=external_id, name=row.Unit.unit_number, \
                createdAt=Validator.dateValidator(row.Unit.created_date), updatedAt=Validator.dateValidator(row.Unit.updated_date)))
            if row.UnitSpace:
                # Building the Unit Room Response using the UnitSpace Model
                location_response.append(UnitRoom(communityId=row.UnitSpace.community_id, \
                externalId=row.UnitSpace.external_id, unitspaceId=row.UnitSpace.unitspace_id,\
                parentIdExternal=row.Unit.external_id, name=row.UnitSpace.unitspace_number, \
                createdAt=Validator.dateValidator(row.UnitSpace.created_date), updatedAt=Validator.dateValidator(row.UnitSpace.updated_date)))

        return location_response, paginate_response

