from datetime import datetime

from IOTShared.Controller.IOTEventController import IOTEventController
from VendorShared.Utilities.VendorConstants import VendorConstants
from VendorShared.Utilities.Utils import delta_of_data, format_phone
from VendorShared.Model.ServiceRequest import ServiceRequest
from ResmanShared.Model.ResmanResponse import CurrentResidentResponse, LeaseResponse
from DataPushPullShared.Utilities.Entities import Person, Addres, Resident, Lease, LeaseInterval, RentableItem, Unit
from ResidentShared.Repository.ResidentRepository import ResidentRespository
from LeaseManagementShared.Repository.LeaseRepository import LeaseRespository
from LocationShared.Repository.LocationRepository import LocationRespository
from ResidentShared.Model.ResidentResponse import ResidentImportResponse
from LocationShared.Model.LocationResponse import LocationImportResponse
from LeaseManagementShared.Models.LeaseResponse import LeaseImportResponse
from ResmanShared.Utilities.ResmanConstants import ResmanConstants


class ResmanMapper:

    def __init__(self, service_request:ServiceRequest):
        self.service_request = service_request
        self.iot_controller = IOTEventController(service_request)

    def residents_mapper(self, resident_response:CurrentResidentResponse):
        """
        Mapping the Resman Resident Response with Unit table
        """
        community_id = self.service_request.payload[VendorConstants.COMMUNITY_UUID]
        customer_id = self.service_request.payload[VendorConstants.CUSTOMER_UUID]
        resman_response = ResidentImportResponse()
        session = self.service_request.outgoing.sql.get(VendorConstants.MDM_DB).session()
        dao = ResidentRespository(session, customer_id, community_id, service_request=self.service_request)
        for resident in resident_response.Residents:
            # Insert/Update data to Person Table
            is_update = False
            is_insert = False
            person_obj = Person(
                customer_id=customer_id,
                community_id=community_id,
                external_id=resident.PersonID,
                first_name=resident.FirstName,
                last_name=resident.LastName,
                email_address=resident.Email,
                date_of_birth=datetime.strptime(resident.Birthdate, '%Y-%m-%d').date() if resident.Birthdate else None,
                mobile_phone=format_phone(resident.MobilePhone) if resident.MobilePhone else None,
                home_phone=format_phone(resident.HomePhone) if resident.HomePhone else None,
                work_phone=format_phone(resident.WorkPhone) if resident.WorkPhone else None,
            )
            person_result = dao.get_person(resident.PersonID)
            if person_result:
                person_id = person_result.person_id
                update_table, update_dict = delta_of_data(person_obj, person_result)
                if update_table:
                    dao.update_person(person_id, update_dict)
                    resman_response.person.update += 1
                    is_update = True
            else:
                person_id = dao.save_person(person_obj)
                resman_response.person.insert += 1
                is_insert = True
            # Insert/Update data to Resident Table
            resident_obj = Resident(
                customer_id=customer_id,
                community_id=community_id,
                person_id=person_id,
                external_id=resident.PersonID,
                is_primary_contact=resident.MainContact,
                is_minor=resident.IsMinor
            )
            resident_result = dao.get_resident(person_id)
            if resident_result:
                resident_id = resident_result.resident_id
                update_table, update_dict = delta_of_data(resident_obj, resident_result)
                if update_table:
                    dao.update_resident(resident_id, update_dict)
                    resman_response.resident.update += 1
                    is_update = True
            else:
                resident_id = dao.save_resident(resident_obj)
                resman_response.resident.insert += 1

            event_type = None
            if is_insert:
                event_type = VendorConstants.ADD
            elif is_update:
                event_type = VendorConstants.MOD

            if event_type:
                self.iot_controller.send_resident_event(person_obj, resident_obj, event_type)
            # Insert/Update data to Address Table
            address_obj = Addres(
                customer_id=customer_id,
                community_id=community_id,
                person_id=person_id,
                unit_number=resident.Unit,
                building=resident.Building
            )
            address_result = dao.get_address(person_id)
            if address_result:
                address_id = address_result.address_id
                update_table, update_dict = delta_of_data(address_obj, address_result)
                if update_table:
                    dao.update_address(address_id, update_dict)
                    resman_response.address.update += 1                    
            else:
                address_id = dao.save_address(address_obj)
                resman_response.address.insert += 1            
        session.close()
        return resman_response
    
    def leases_mapper(self, person_response:LeaseResponse):
        """
        Mapping the Resman leases Response with Unit table
        """
        community_id = self.service_request.payload[VendorConstants.COMMUNITY_UUID]
        customer_id = self.service_request.payload[VendorConstants.CUSTOMER_UUID]
        resman_response = LeaseImportResponse()
        session = self.service_request.outgoing.sql.get(VendorConstants.MDM_DB).session()
        dao = LeaseRespository(session, customer_id, community_id, service_request=self.service_request)
        location_dao = LocationRespository(session, customer_id, community_id, service_request=self.service_request)
        resident_dao = ResidentRespository(session, customer_id, community_id, service_request=self.service_request)
        for i in person_response.People:
            unit_result = location_dao.get_unit_by_unit_number_and_building(i.Unit, i.Building)
            unit_id = unit_result and unit_result.unit_id
            is_insert = None
            is_update = None
            if not unit_id:
                unit_obj = Unit(
                    customer_id=customer_id,
                    community_id=community_id,
                    unit_number=i.Unit,
                    building=i.Building,
                    is_featured = False,
                    is_furnished = False,
                    is_corporate_rented = False
                    )
                unit_id = location_dao.save_unit(unit_obj)
                resman_response.locations.insert += 1
                self.iot_controller.send_location_event(unit_obj, VendorConstants.ADD)
            person_result = resident_dao.get_person(i.PersonID)
            person_id = person_result and person_result.person_id
            if not person_id:
                person_obj = Person(
                    customer_id=customer_id,
                    community_id=community_id,
                    external_id=i.PersonID,
                    first_name=i.FirstName,
                    last_name=i.LastName,
                    email_address=i.Email,
                    date_of_birth=datetime.strptime(i.Birthdate, '%Y-%m-%d').date() if i.Birthdate else None,
                    mobile_phone=format_phone(i.MobilePhone) if i.MobilePhone else None,
                    home_phone=format_phone(i.HomePhone) if i.HomePhone else None,
                    work_phone=format_phone(i.WorkPhone) if i.WorkPhone else None
                )
                person_id = resident_dao.save_person(person_obj)
                resman_response.person.insert += 1
                resident_obj = Resident(
                    customer_id=customer_id,
                    community_id=community_id,
                    person_id=person_id,
                    external_id=i.PersonID,
                    is_primary_contact=i.MainContact
                )
                resident_id = resident_dao.save_resident(resident_obj)
                resman_response.resident.insert += 1
                self.iot_controller.send_resident_event(person_obj, resident_obj, VendorConstants.ADD)
                address_obj = Addres(
                    customer_id=customer_id,
                    community_id=community_id,
                    person_id=person_id,
                    unit_number=i.Unit,
                    building=i.Building
                )
                address_id = resident_dao.save_address(address_obj)
                resman_response.address.insert += 1
            # Insert/Update data to Lease Table
            lease_obj = Lease(
                external_id = i.LeaseID,
                customer_id=customer_id,
                community_id=community_id,
                move_out_date=i.MoveOutDate and datetime.strptime(i.MoveOutDate, '%Y-%m-%d').date() or None,
                move_in_date=i.MoveInDate and datetime.strptime(i.MoveInDate, '%Y-%m-%d').date() or None,
                unit_id=unit_id,
                person_id=person_id,
                lease_status=i.Status
            )
            lease_result = dao.get_lease(i.LeaseID, person_id)
            if lease_result:
                lease_id = lease_result.lease_id
                update_table, update_dict = delta_of_data(lease_obj, lease_result)
                if update_table:
                    dao.update_lease(lease_id, update_dict)
                    resman_response.lease.update += 1
                    is_update = True
            else:
                lease_id = dao.save_lease(lease_obj)
                resman_response.lease.insert += 1
                is_insert = True
            # Insert/Update data to Lease Interval Table leases_history.LeaseEndDate
            lease_interval = []
            for leases_history in i.Leases:
                if leases_history.Status != ResmanConstants.PENDING_RENEWAL:
                    lease_interval_obj = LeaseInterval(
                    customer_id=customer_id,
                    community_id=community_id,
                    lease_id=lease_id,
                    external_id=leases_history.LeaseID,
                    lease_interval_status= leases_history.Status,
                    end_date=leases_history.LeaseEndDate and datetime.strptime(leases_history.LeaseEndDate, '%Y-%m-%d').date() or None,
                    start_date=leases_history.LeaseStartDate and datetime.strptime(leases_history.LeaseStartDate, '%Y-%m-%d').date() or None,
                    )
                    lease_int_result = dao.get_lease_interval(lease_id, leases_history.LeaseID)
                    if lease_int_result:
                        lease_interval_id = lease_int_result.lease_interval_id
                        update_table, update_dict = delta_of_data(lease_interval_obj, lease_int_result)
                        if update_table:
                            dao.update_lease_interval(lease_interval_id, update_dict)
                            resman_response.lease_interval.update += 1
                            is_update = True
                            lease_interval.append(lease_interval_obj)
                    else:
                        lease_interval_id = dao.save_lease_interval(lease_interval_obj)
                        resman_response.lease_interval.insert += 1
                        is_update = True
                        lease_interval.append(lease_interval_obj)
            
            event_type = None
            if is_insert:
                event_type = VendorConstants.ADD
            elif is_update:
                event_type = VendorConstants.MOD

            if event_type:
                self.iot_controller.send_lease_event(lease_obj, lease_interval, event_type)
        session.close()
        return resman_response
    
    def location_mapper(self, location_list:list):
        """
        Mapping the Resman location Response with Unit table
        """
        community_id = self.service_request.payload[VendorConstants.COMMUNITY_UUID]
        customer_id = self.service_request.payload[VendorConstants.CUSTOMER_UUID]
        resman_response = LocationImportResponse()
        session = self.service_request.outgoing.sql.get(VendorConstants.MDM_DB).session()
        dao = LocationRespository(session, customer_id, community_id, service_request=self.service_request)
        # Insert/Update data to Unit Table
        for i in location_list:
            is_update = False
            is_insert = False
            externalId="{}-{}-{}-{}".format(community_id, i.Building, \
            i.Floor, i.UnitNumber)
            unit_obj = Unit(
                customer_id=customer_id,
                community_id=community_id,
                unit_number=i.UnitNumber,
                unit_type=i.UnitType,
                external_id=externalId,
                building=i.Building,
                floor_plan=i.Floor,
                is_featured = False,
                is_furnished = False,
                is_corporate_rented = False,
                street_1=i.StreetAddress,
                city=i.City,
                state=i.State,
                zipcode=i.Zip,
                country= VendorConstants.US if i.Zip else None
            )
            #unit_result = dao.get_units(i.UnitId)
            unit_result = dao.get_unit_by_unit_number_and_building(i.UnitNumber, i.Building)
            if unit_result:
                unit_id = unit_result.unit_id
                update_table, update_dict = delta_of_data(unit_obj, unit_result)
                if update_table:
                    dao.update_unit(unit_id, update_dict)
                    resman_response.locations.update += 1
                    is_update = True
            else:
                unit_id = dao.save_unit(unit_obj)
                resman_response.locations.insert += 1
                is_insert = True

            event_type = None
            if is_insert:
                event_type = VendorConstants.ADD
            elif is_update:
                event_type = VendorConstants.MOD

            if event_type:
                self.iot_controller.send_location_event(unit_obj, event_type)
        session.close()
        return resman_response
