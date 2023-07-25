from datetime import datetime

from IOTShared.Controller.IOTEventController import IOTEventController
from LocationShared.Model.LocationResponse import LocationImportResponse
from LocationShared.Repository.LocationRepository import LocationRespository
from VendorShared.Model.ServiceRequest import ServiceRequest
from VendorShared.Utilities.VendorConstants import VendorConstants
from VendorShared.Utilities.Utils import delta_of_data, format_phone
from ResidentShared.Repository.ResidentRepository import ResidentRespository
from ResidentShared.Model.ResidentResponse import ResidentImportResponse
from DataPushPullShared.Utilities.Entities import Person, Addres, Resident, Unit, Lease, LeaseInterval, UnitSpace
from LeaseManagementShared.Models.LeaseResponse import LeaseImportResponse
from LeaseManagementShared.Repository.LeaseRepository import LeaseRespository
from EntrataShared.Model.EntrataResponse import Leases
from EntrataShared.Utilities.EntrataConstants import EntrataConstants


class EntrataMapper:

    def __init__(self, service_request:ServiceRequest):
        self.service_request = service_request
        self.iot_controller = IOTEventController(service_request)

    def location_mapper(self, location_list: list):
        """
        Mapping the Entrata Location Response with the Unit table
        """
        community_id = self.service_request.payload[VendorConstants.COMMUNITY_UUID]
        customer_id = self.service_request.payload[VendorConstants.CUSTOMER_UUID]
        entrata_response = LocationImportResponse()
        session = self.service_request.outgoing.sql.get(VendorConstants.MDM_DB).session()
        dao = LocationRespository(session, customer_id, community_id,  service_request=self.service_request)
        # Insert/Update Data to Unit Table
        for i in location_list:
            is_update = False
            is_insert = False
            unit_obj = Unit(
                     customer_id = customer_id,
                     community_id = community_id,
                     unit_number = i.unitNumber,
                     unit_type = i.unitTypeId,
                     external_id = i.id,
                     building = i.buildingId,
                     unit_name = i.buildingName,
                     floor_plan = i.floorplanId,
                     num_bedrooms = i.numberOfBedrooms,
                     num_bathrooms = i.numberOfBathrooms,
                     number_of_occupants = i.maxNumberOccupants,
                     is_featured = False,
                     is_furnished = False if "0" == i.isFurnished else True,
                     is_corporate_rented = False if "0" == i.isCorporateRented else True,
                     street_1 = i.unitAddress.address,
                     city = i.unitAddress.city,
                     state = i.unitAddress.state,
                     zipcode = i.unitAddress.postalCode,
                     country = VendorConstants.US if i.unitAddress.postalCode else None
            )
            unit_result = dao.get_units(i.id)
            if unit_result:
                unit_id = unit_result.unit_id
                update_table, update_dict = delta_of_data(unit_obj, unit_result)
                if update_table:
                    dao.update_unit(unit_id, update_dict)
                    entrata_response.locations.update += 1
                    is_update = True
            else:
                unit_id = dao.save_unit(unit_obj)
                entrata_response.locations.insert += 1
                is_insert = True

            unit_space_list = []
            for unit_space in i.unitSpaces.unitSpace:
                unitspace_obj = UnitSpace(
                         customer_id = customer_id,
                         community_id = community_id,
                         external_id = str(unit_space.unitSpaceId),
                         unitspace_number = unit_space.unitNumber,
                         unit_id = unit_id,
                         space_configuration = unit_space.spaceConfiguration
                )
                unitspace_result = dao.get_space_units(str(unit_space.unitSpaceId))
                if unitspace_result:
                    unitspace_id = unitspace_result.unitspace_id
                    update_table, update_dict = delta_of_data(unitspace_obj, unitspace_result)
                    if update_table:
                        dao.update_space_unit(unitspace_id, update_dict)
                        entrata_response.unitspace.update += 1
                        unitspace_obj.__setattr__('is_update',True)

                        unit_space_list.append(unitspace_obj)
                else:
                    unitspace_id = dao.save_space_unit(unitspace_obj)
                    entrata_response.unitspace.insert += 1
                    unitspace_obj.__setattr__('is_insert',True)
                    unit_space_list.append(unitspace_obj)
            
            event_type = None
            if is_insert:
                event_type = VendorConstants.ADD
            elif is_update:
                event_type = VendorConstants.MOD

            if event_type or unit_space_list:
                self.iot_controller.send_location_event(unit_obj, event_type, unit_space_list)
        session.close()
        return entrata_response
    
    def resident_mapper(self, resident_list: list):
        """
        Mapping the Entrata Resident Response with the Person, Resident, Address table
        """
        community_id = self.service_request.payload[VendorConstants.COMMUNITY_UUID]
        customer_id = self.service_request.payload[VendorConstants.CUSTOMER_UUID]
        entrata_response = ResidentImportResponse()
        session = self.service_request.outgoing.sql.get(VendorConstants.MDM_DB).session()
        dao = ResidentRespository(session, customer_id, community_id,  service_request=self.service_request)
        for resident in resident_list:
            # Insert/Update data to Person Table
            is_update = False
            is_insert = False
            person_obj = Person(
                customer_id=customer_id,
                community_id=community_id,
                external_id=resident.attributes["Id"],
                first_name=resident.FirstName,
                last_name=resident.LastName,
                email_address=resident.Email,
                date_of_birth=None,
                mobile_phone=format_phone(resident.PhoneNumber) if resident.PhoneNumber else None,
                home_phone=None,
                work_phone=None,
            )
            person_result = dao.get_person(resident.attributes["Id"])
            if person_result:
                person_id = person_result.person_id
                update_table, update_dict = delta_of_data(person_obj, person_result)
                if update_table:
                    dao.update_person(person_id, update_dict)
                    entrata_response.person.update += 1
                    is_update = True
            else:
                person_id = dao.save_person(person_obj)
                entrata_response.person.insert += 1
                is_insert = True
            # Insert/Update data to Resident Table
            resident_obj = Resident(
                customer_id=customer_id,
                community_id=community_id,
                person_id=person_id,
                external_id=resident.attributes["Id"],
                is_primary_contact=True if "Primary" in resident.LeaseId["CustomerType"] else False
            )
            resident_result = dao.get_resident(person_id)
            if resident_result:
                resident_id = resident_result.resident_id
                update_table, update_dict = delta_of_data(resident_obj, resident_result)
                if update_table:
                    dao.update_resident(resident_id, update_dict)
                    entrata_response.resident.update += 1
                    is_update = True
            else:
                resident_id = dao.save_resident(resident_obj)
                entrata_response.resident.insert += 1

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
                unit_number=resident.UnitNumber,
                building=resident.BuildingName,
                street_1=resident.Address,
                city=resident.City,
                state=resident.State,
                zipcode=resident.PostalCode,
                country=VendorConstants.US if resident.PostalCode else None
            )
            address_result = dao.get_address(person_id)
            if address_result:
                address_id = address_result.address_id
                update_table, update_dict = delta_of_data(address_obj, address_result)
                if update_table:
                    dao.update_address(address_id, update_dict)
                    entrata_response.address.update += 1
            else:
                address_id = dao.save_address(address_obj)
                entrata_response.address.insert += 1
        session.close()
        return entrata_response
    
    def leases_mapper(self, leases_response:Leases):
        """
        Mapping the Resman leases Response with Unit table
        """
        community_id = self.service_request.payload[VendorConstants.COMMUNITY_UUID]
        customer_id = self.service_request.payload[VendorConstants.CUSTOMER_UUID]
        entrata_response = LeaseImportResponse()
        session = self.service_request.outgoing.sql.get(VendorConstants.MDM_DB).session()
        dao = LeaseRespository(session, customer_id, community_id, service_request=self.service_request)
        location_dao = LocationRespository(session, customer_id, community_id, service_request=self.service_request)
        resident_dao = ResidentRespository(session, customer_id, community_id, service_request=self.service_request)
        for i in leases_response.lease:
            for customer in i.customers.customer:
                if customer.customerType == "Primary":
                    is_insert = None
                    is_update = None
                    event_type = None
                    unit_obj = Unit(
                        customer_id = customer_id,
                        community_id = community_id,
                        external_id = i.unitId,
                        building = i.buildingId,
                        unit_name = i.buildingName,
                        unit_number = i.unitNumberSpace.split('-')[0],
                        floor_plan = i.floorPlanId,
                        is_featured = False,
                        is_furnished = False,
                        is_corporate_rented = False
                    )
                    unit_result = location_dao.get_units(i.unitId)
                    if unit_result:
                        unit_id = unit_result.unit_id
                        update_table, update_dict = delta_of_data(unit_obj, unit_result)
                        if update_table:
                            location_dao.update_unit(unit_id, update_dict)
                            entrata_response.locations.update += 1
                            event_type = VendorConstants.MOD
                    else:
                        unit_id = location_dao.save_unit(unit_obj)
                        entrata_response.locations.insert += 1
                        event_type = VendorConstants.ADD
                    unit_space_list = []
                    unitspace_obj = UnitSpace(
                             customer_id = customer_id,
                             community_id = community_id,
                             external_id = i.unitSpaceId,
                             unitspace_number = i.unitNumberSpace,
                             unit_id = unit_id,
                             space_configuration = i.spaceConfiguration
                    )
                    unitspace_result = location_dao.get_space_units(i.unitSpaceId)
                    if unitspace_result:
                        unitspace_id = unitspace_result.unitspace_id
                        update_table, update_dict = delta_of_data(unitspace_obj, unitspace_result)
                        if update_table:
                            location_dao.update_space_unit(unitspace_id, update_dict)
                            entrata_response.unitspace.update += 1
                            unitspace_obj.unitspace_id = unitspace_id
                            unitspace_obj.__setattr__('is_update',True)
                            unit_space_list.append(unitspace_obj)
                    else:
                        unitspace_id = location_dao.save_space_unit(unitspace_obj)
                        entrata_response.unitspace.insert += 1
                        unitspace_obj.unitspace_id = unitspace_id
                        unitspace_obj.__setattr__('is_insert',True)
                        unit_space_list.append(unitspace_obj)
                    self.iot_controller.send_location_event(unit_obj, event_type, unit_space_list)
                    person_result = resident_dao.get_person(customer.id)
                    person_id = person_result and person_result.person_id
                    if not person_id:
                        person_obj = Person(
                            customer_id=customer_id,
                            community_id=community_id,
                            external_id=customer.id,
                            first_name=customer.firstName,
                            last_name=customer.lastName,
                            email_address=customer.addresses.address.email,
                            date_of_birth=None,
                            mobile_phone=format_phone(customer.phone.phoneNumber) if customer.phone.phoneNumber else None,
                            home_phone=None,
                            work_phone=None,
                        )
                        person_id = resident_dao.save_person(person_obj)
                        entrata_response.person.insert += 1
                        resident_obj = Resident(
                            customer_id=customer_id,
                            community_id=community_id,
                            person_id=person_id,
                            external_id=customer.id,
                            is_primary_contact=True
                        )
                        resident_id = resident_dao.save_resident(resident_obj)
                        entrata_response.resident.insert += 1
                        self.iot_controller.send_resident_event(person_obj, resident_obj, VendorConstants.ADD)
                        address_obj = Addres(
                            customer_id=customer_id,
                            community_id=community_id,
                            person_id=person_id,
                            building=i.buildingName,
                            street_1=customer.addresses.address.streetLine,
                            city=customer.addresses.address.city,
                            state=customer.addresses.address.state,
                            zipcode=customer.addresses.address.postalCode,
                            country=VendorConstants.US if customer.addresses.address.postalCode else None
                        )
                        address_id = resident_dao.save_address(address_obj)
                        entrata_response.address.insert += 1
                    lease_signed_on = None
                    for activites in i.leaseActivities.leasesActivity:
                        if activites.eventType.lower()=="leasesigned":
                            lease_signed_on = activites.date
                    # Insert/Update data to Lease Table
                    lease_obj = Lease(
                        external_id = i.id,
                        customer_id=customer_id,
                        community_id=community_id,
                        lease_type=i.leaseType,
                        lease_status=i.leaseIntervalStatus,
                        unit_id=unit_id,
                        person_id=person_id,
                        occupany_type=i.occupancyType,
                        building_name=i.buildingName,
                        floor_plan=i.floorPlanId if i.floorPlanId else i.floorPlanName,
                        unit=i.unitId,
                        unit_space=i.spaceConfiguration,
                        unitspace_id=unitspace_id,
                        unitspace_number=i.unitNumberSpace,
                        lease_signed_date = lease_signed_on and \
                                datetime.strptime(lease_signed_on, '%Y-%m-%d').date() or None,
                        move_out_date=(customer.moveOutDate and datetime.strptime(customer.moveOutDate, '%Y-%m-%d').date() \
                                                or None) if customer.leaseCustomerStatus == "Notice" else None, 
                        move_in_date=customer.moveInDate and datetime.strptime(customer.moveInDate, '%Y-%m-%d').date() or None,
                        notice_to_vacate_date= (customer.moveOutDate and datetime.strptime(customer.moveOutDate, '%Y-%m-%d').date() \
                                                or None) if customer.leaseCustomerStatus == "Notice" else None,                                                 
                        termination_start_date= i.terminationStartDate and \
                            datetime.strptime(i.terminationStartDate, '%Y-%m-%d').date() or None,
                    )
                    lease_result = dao.get_lease(i.id, person_id)
                    if lease_result:
                        lease_id = lease_result.lease_id
                        lease_obj.lease_id = lease_id
                        update_table, update_dict = delta_of_data(lease_obj, lease_result)
                        if update_table:
                            dao.update_lease(lease_id, update_dict)
                            entrata_response.lease.update += 1
                            is_update = True
                    else:
                        lease_id = dao.save_lease(lease_obj)
                        lease_obj.lease_id = lease_id
                        entrata_response.lease.insert += 1
                        is_insert = True
                    # Insert/Update data to Lease Interval Table
                    lease_interval = []
                    for leases_interval in i.leaseIntervals.leaseInterval:
                        if leases_interval.leaseIntervalStatusTypeName != EntrataConstants.CANCELLED:
                            if leases_interval.leaseIntervalTypeName and leases_interval.leaseApprovedOn:
                                lease_interval_obj = LeaseInterval(
                                    customer_id=customer_id,
                                    community_id=community_id,
                                    external_id=leases_interval.id,
                                    lease_id=lease_id,
                                    start_date=leases_interval.startDate and \
                                        datetime.strptime(leases_interval.startDate, '%Y-%m-%d').date() or None,
                                    end_date=leases_interval.endDate and \
                                        datetime.strptime(leases_interval.endDate, '%Y-%m-%d').date() or None,
                                    lease_interval_type_name=leases_interval.leaseIntervalTypeName,
                                    lease_interval_status=leases_interval.leaseIntervalStatusTypeName,
                                    lease_approved_on=leases_interval.leaseApprovedOn and \
                                        datetime.strptime(leases_interval.leaseApprovedOn, '%Y-%m-%d').date() or None,
                                    application_completed_on=leases_interval.applicationCompletedOn and \
                                        datetime.strptime(leases_interval.applicationCompletedOn, '%Y-%m-%d').date() or None,
                                    external_application_id=leases_interval.applicationId,
                                )
                                lease_int_result = dao.get_lease_interval(lease_id, leases_interval.id)
                                if lease_int_result:
                                    lease_interval_id = lease_int_result.lease_interval_id
                                    update_table, update_dict = delta_of_data(lease_interval_obj, lease_int_result)
                                    if update_table:
                                        dao.update_lease_interval(lease_interval_id, update_dict)
                                        entrata_response.lease_interval.update += 1
                                        is_update = True
                                        lease_interval.append(lease_interval_obj)
                                else:
                                    lease_interval_id = dao.save_lease_interval(lease_interval_obj)
                                    entrata_response.lease_interval.insert += 1
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
        return entrata_response
