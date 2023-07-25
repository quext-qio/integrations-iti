from DataPushPullShared.Utilities.DataController import DataValidation, Schema, date_filter
from DataPushPullShared.Utilities.Convert import Convert
from VendorShared.Model.ServiceRequest import ServiceRequest
from VendorShared.Utilities.VendorConstants import VendorConstants
from ExceptionHandling.Utilities.ErrorCode import ErrorCode
from ExceptionHandling.Model.Exceptions import ValidationError
from DataPushPullShared.Utilities.Entities import Lease, LeaseInterval, RentableItem, Person, Unit, UnitSpace
from LeaseManagementShared.Models.LeaseResponse import Lease as qLease
from DataPushPullShared.Utilities.DataController import QuextIntegrationConstants
from sqlalchemy import and_, func
from sqlalchemy_paginator import Paginator


class LeasingController:
    """
        Handles the Generic validation and returns the 
        respective vendors Object(Resman,Realpage)
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

    def get_leases(self, servicerequest: ServiceRequest):
        """
        Returns the Leasing Endpoint results by resolving the Vendor using the factory design
        pattern and implement the respective third party endpoint.
    
        Parameters
        ----------
        servicerequest: Zato Request Object
        """
        # validating input request
        leases = []
        self.__validate(servicerequest = servicerequest)
        session = servicerequest.outgoing.sql.get(VendorConstants.MDM_DB).session()

        t = session.query(
                LeaseInterval.lease_id,
                func.min(LeaseInterval.start_date).label('min_time'),
            ).group_by(LeaseInterval.lease_id)
        subquery = t.subquery()

        t1 = session.query(
                LeaseInterval.lease_id,
                func.max(LeaseInterval.end_date).label('max_time'),
            ).group_by(LeaseInterval.lease_id).subquery('t1')

        Query  = session.query(
                    Lease, LeaseInterval, Person, Unit, UnitSpace, RentableItem, subquery.c.min_time).filter(and_(
                    Lease.lease_id == LeaseInterval.lease_id, Lease.lease_id == t1.c.lease_id,
                    LeaseInterval.end_date == t1.c.max_time)).join(Person,
                    Lease.person_id == Person.person_id, isouter=True).join(Unit,
                    Lease.unit_id == Unit.unit_id, isouter=True).join(UnitSpace,
                    Lease.unitspace_id == UnitSpace.unitspace_id, isouter=True).join(RentableItem,
                    Lease.lease_id == RentableItem.lease_id, isouter=True).join(subquery, Lease.lease_id==subquery.c.lease_id).filter(
                    and_(Lease.customer_id==(servicerequest.payload[VendorConstants.CUSTOMER_UUID]),
                    Lease.community_id==(servicerequest.payload[VendorConstants.COMMUNITY_UUID]))
                )

         # will print the compiled query statement againt the dialect.
        Query = date_filter(Lease, Query, servicerequest)
        paginator = Paginator(Query, QuextIntegrationConstants.DEFAULT_LIMIT)
        paginate_response = {
            QuextIntegrationConstants.TOTAL_PAGES: paginator.total_pages,
            QuextIntegrationConstants.CURRENT_PAGE: servicerequest.page
        }
        if servicerequest.page < 1 or servicerequest.page > paginator.total_pages:
            return  leases, paginate_response
        page = paginator.page(servicerequest.page)
        session.close()
        Validator = Convert()
        for r in  page.object_list:
            lease_status = self.lease_status_mapping(r.LeaseInterval.lease_interval_status)
            if not r.Lease.move_in_date:
                lease_status = VendorConstants.PENDING
            lease = qLease(
                        communityId = r.Lease.community_id,
                        externalId = r.Lease.external_id,
                        personIdExternal = r.Person is not None and r.Person.external_id or None,
                        locationIdExternal = r.UnitSpace is not None and r.UnitSpace.external_id \
                                            or r.Unit is not None and r.Unit.external_id or None,
                        startDate = r.min_time is not None and Validator.dateValidator(r.min_time) or None,
                        endDate = r.LeaseInterval is not None  and Validator.dateValidator(r.LeaseInterval.end_date) or None,
                        moveInDate = Validator.dateValidator(r.Lease.move_in_date),
                        moveOutDate = Validator.dateValidator(r.LeaseInterval.end_date),
                        status = lease_status,
                        leaseId = r.Lease.lease_id,
                        createdAt = Validator.dateValidator(r.Lease.created_date),
                        updatedAt = Validator.dateValidator(r.Lease.updated_date),
                        personId = r.Person is not None  and r.Person.person_id,
                        locationId = r.UnitSpace is not None  and r.UnitSpace.unitspace_id \
                                    or r.Unit is not None and r.Unit.unit_id or None
                    )
            leases.append(lease)
        return leases, paginate_response

    def lease_status_mapping(self, lease_status):
        """
        Current - Active
        Notice - Active
        Future - Active
        Pending/Pending Transfer - Queued
        Evicted - Terminated
        past - Archived
        """
        switcher = {
            VendorConstants.CURRENT: VendorConstants.ACTIVE,
            VendorConstants.FUTURE: VendorConstants.ACTIVE,
            VendorConstants.NOTICE: VendorConstants.ACTIVE,
            VendorConstants.PENDING: VendorConstants.QUEUED,
            VendorConstants.PENDINGT: VendorConstants.QUEUED,
            VendorConstants.EVICTED: VendorConstants.TERMINATED,
            VendorConstants.PAST: VendorConstants.ARCHIVED
        }
        lease_status = switcher.get(lease_status, None)
        return lease_status

