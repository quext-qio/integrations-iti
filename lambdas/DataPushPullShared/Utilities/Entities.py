from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Integer, String, text


from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Person(Base):
    __tablename__ = 'person'
    __table_args__ = (
        Index('person_customer_community_idx', 'customer_id', 'community_id'),
        {'schema': 'mdm'}
    )

    person_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"), comment='Person Record Identifier')
    customer_id = Column(UUID, comment='Quext Customer UUID')
    community_id = Column(UUID, comment='Quext Community UUID')
    external_id = Column(String, index=True, comment='External Id Reference')
    first_name = Column(String, nullable=False, comment='First name of the person')
    middle_name = Column(String, comment='Middle name of the person')
    last_name = Column(String, nullable=False, comment='Last name of the person')
    preferred_name = Column(String, comment='Preferred name of the person')
    date_of_birth = Column(Date, comment='Date of birth of the person')
    email_address = Column(String, comment='Email Address')
    home_phone = Column(String, comment='Home Phone Number')
    mobile_phone = Column(String, comment='Mobile/Cell Phone Number')
    work_phone = Column(String, comment='Work Phone Number')
    is_deleted = Column(Boolean, server_default=text("false"), comment='Flag for soft delete of record')
    created_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record created timestamp')
    updated_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record updated timestamp')

class Unit(Base):
    __tablename__ = 'unit'
    __table_args__ = {'schema': 'mdm'}

    unit_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"), comment='Unit Record Identifier')
    customer_id = Column(UUID, nullable=False, comment='Quext Customer UUID')
    community_id = Column(UUID, nullable=False, comment='Quext Community UUID')
    external_id = Column(String, comment='External Id Reference')
    external_property_id = Column(String, comment='External Property Id Reference')
    unit_name = Column(String, comment='Name of the Unit')
    unit_number = Column(String, comment='Unit number or name')
    unit_type = Column(String, comment='Unit Type')
    floor_plan = Column(String, comment='Floor Number or Name')
    building = Column(String, comment='Building Number or Name')
    street_1 = Column(String, comment='Street Line 1 of the Address')
    street_2 = Column(String, comment='Street Line 2 of the Address')
    street_3 = Column(String, comment='Street Line 3 of the Address')
    city = Column(String, comment='City Name')
    state = Column(String, comment='State or Provinces')
    country = Column(String, comment='Country Name')
    zipcode = Column(String, comment='Zipcode')
    num_bedrooms = Column(Integer, comment='Number of bedrooms')
    num_bathrooms = Column(Integer, comment='Number of bath rooms')
    active = Column(Boolean, nullable=False, server_default=text("true"), comment='Status of the Unit')
    is_featured = Column(Boolean, nullable=False, server_default=text("true"), comment='If Featured flag for the Unit')
    is_furnished = Column(Boolean, nullable=False, server_default=text("true"), comment='Indicates about furnished or not')
    is_corporate_rented = Column(Boolean, nullable=False, server_default=text("true"), comment='Indicates about corporate rented or not')
    number_of_occupants = Column(Integer, comment='Number of Occupants')
    square_feet = Column(Integer, comment='Area of the unit')
    manager = Column(String, comment='Marketing Manager or Team Name')
    website = Column(String, comment='Website address of the Unit')
    year_built = Column(Integer, comment='Built year of the Unit')
    description = Column(String, comment='Description about the Unit')
    is_deleted = Column(Boolean, server_default=text("false"), comment='Flag for soft delete of record')
    created_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record created timestamp')
    updated_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record updated timestamp')

class UnitSpace(Base):
    __tablename__ = 'unitspace'
    __table_args__ = {'schema': 'mdm'}

    unitspace_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"), comment='UnitSpace Record Identifier')
    customer_id = Column(UUID, comment='Quext Customer UUID')
    community_id = Column(UUID, comment='Quext Community UUID')
    external_id = Column(String, index=True, comment='External Id Reference')
    unit_id = Column(ForeignKey('mdm.unit.unit_id'), index=True, comment='Unit UUID from Unit Table')
    unitspace_number = Column(String, comment='Unit Space information')
    space_configuration = Column(String, comment='Unit Space Configuraton Information')
    is_deleted = Column(Boolean, server_default=text("false"), comment='Flag for soft delete of record')
    created_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record created timestamp')
    updated_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record updated timestamp')

    unit = relationship('Unit')

class Addres(Base):
    __tablename__ = 'address'
    __table_args__ = {'schema': 'mdm'}

    address_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"), comment='Address Record Identifier')
    customer_id = Column(UUID, comment='Quext Customer UUID')
    community_id = Column(UUID, comment='Quext Community UUID')
    external_id = Column(String, index=True, comment='External Id Reference')
    person_id = Column(ForeignKey('mdm.person.person_id', ondelete='CASCADE', onupdate='CASCADE'), comment='Quext Person UUID from person table')
    address_type = Column(String, comment='Address Type')
    unit_number = Column(String, comment='Unit number or name')
    unit_type = Column(String, comment='Unit Type')
    floor_plan = Column(String, comment='Floor Number or Name')
    building = Column(String, comment='Building Number or Name')
    street_1 = Column(String, comment='Street Line 1 of the Address')
    street_2 = Column(String, comment='Street Line 2 of the Address')
    street_3 = Column(String, comment='Street Line 3 of the Address')
    city = Column(String, comment='City Name')
    state = Column(String, comment='State or Provinces')
    country = Column(String, comment='Country Name')
    zipcode = Column(String, comment='Zipcode')
    created_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record created timestamp')
    updated_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record updated timestamp')

    person = relationship('Person')


class Applicant(Base):
    __tablename__ = 'applicant'
    __table_args__ = {'schema': 'mdm'}

    applicant_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"), comment='Applicant Record Identifier')
    customer_id = Column(UUID, comment='Quext Customer UUID')
    community_id = Column(UUID, comment='Quext Community UUID')
    person_id = Column(ForeignKey('mdm.person.person_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, comment='Person Record Identifier')
    external_id = Column(String, index=True, comment='External Id Reference for applicant')
    created_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record created timestamp')
    updated_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record updated timestamp')

    person = relationship('Person')


class Lease(Base):
    __tablename__ = 'lease'
    __table_args__ = {'schema': 'mdm'}

    lease_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"), comment='Lease Record Identifier')
    customer_id = Column(UUID, comment='Quext Customer UUID')
    community_id = Column(UUID, comment='Quext Community UUID')
    external_id = Column(String, index=True, comment='External Id Reference')
    external_transfer_lease_id = Column(String, comment='External Lease Transfer Id Reference')
    external_lease_property_id = Column(String, comment='External Lease Property Id Reference')
    lease_type = Column(String, comment='Lease Type')
    lease_status = Column(String, comment='Status of the Lease')
    unit_id = Column(ForeignKey('mdm.unit.unit_id'), index=True, comment='Unit UUID from Unit Table')
    person_id = Column(ForeignKey('mdm.person.person_id'), comment='Person UUID from Person Table')
    occupany_type = Column(String, comment='Occupany Type')
    building_name = Column(String, comment='Building Name')
    floor_plan = Column(String, comment='Floor Plan Name or Id')
    unit = Column(String, comment='Unit Name or Id')
    unit_space = Column(String, comment='Unit Space information')
    unitspace_id = Column(ForeignKey('mdm.unitspace.unitspace_id'), index=True, comment='UnitSpace UUID from UnitSpace Table')
    unitspace_number = Column(String, comment='Unit Space Number information')
    lease_signed_date = Column(Date, comment='Lease Signed Date')
    move_in_date = Column(Date, comment='MoveIn date of the resident')
    move_out_date = Column(Date, comment='MoveOut date of the resident')
    cancellation_date = Column(Date, comment='Lease Cancellation date')
    denial_date = Column(Date, comment='Lease Deniel date')
    scheduled_move_in_date = Column(Date, comment='Scheduled MoveIn date')
    scheduled_move_out_date = Column(Date, comment='Scheduled MoveOut date')
    notice_to_vacate_date = Column(Date, comment='Notice to vacate date')
    termination_start_date = Column(Date, comment='Lease termination date')
    is_deleted = Column(Boolean, server_default=text("false"), comment='Flag for soft delete of record')
    created_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record created timestamp')
    updated_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record updated timestamp')

    person = relationship('Person')
    unit1 = relationship('Unit')


class Resident(Base):
    __tablename__ = 'resident'
    __table_args__ = {'schema': 'mdm'}

    resident_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"), comment='Resident Record Identifier')
    customer_id = Column(UUID, comment='Quext Customer UUID')
    community_id = Column(UUID, comment='Quext Community UUID')
    person_id = Column(ForeignKey('mdm.person.person_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, comment='Person Record Identifier')
    external_id = Column(String, index=True, comment='External Id Reference for resident')
    is_minor = Column(Boolean, server_default=text("false"), comment='Flag indicates whether the resident is minor')
    is_primary_contact = Column(Boolean, server_default=text("true"), comment='Flag indicates whether the resident is primary contact')
    created_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record created timestamp')
    updated_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record updated timestamp')

    person = relationship('Person')


class ApplicantPreference(Base):
    __tablename__ = 'applicant_preference'
    __table_args__ = {'schema': 'mdm'}

    applicant_preference_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"), comment='Applicant Preference Record Identifier')
    customer_id = Column(UUID, comment='Quext Customer UUID')
    community_id = Column(UUID, comment='Quext Community UUID')
    applicant_id = Column(ForeignKey('mdm.applicant.applicant_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, comment='Applicant UUID from Applicant Table')
    external_id = Column(String, comment='External Id Reference')
    desired_move_in_date = Column(Date, comment='Desired MoveIn Date Preference')
    desired_floor_plan_id = Column(String, comment='Desired FloorPlan Preference')
    desired_unit_type_id = Column(String, comment='Desired Unit Type Preference')
    desired_unit_id = Column(String, comment='Desired Unit Preference')
    desired_rent_min = Column(Integer, comment='Desired Rent Minimum Amount Preference')
    desired_rent_max = Column(Integer, comment='Desired Rent Maximum Amount Preference')
    desired_num_bedrooms = Column(Integer, comment='Desired No.of bedrooms Preference')
    desired_num_bathrooms = Column(Integer, comment='Desired No.of bathrooms Preference')
    desired_lease_terms = Column(Integer, comment='Desired Lease terms Preference')
    number_of_occupants = Column(Integer, comment='Desired No.of occupants Preference')
    comment = Column(String, comment='Other comments about the Preference')
    created_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record created timestamp')
    updated_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record updated timestamp')

    applicant = relationship('Applicant')


class LeaseInterval(Base):
    __tablename__ = 'lease_interval'
    __table_args__ = {'schema': 'mdm'}

    lease_interval_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"), comment='Lease Interval Record Identifier')
    customer_id = Column(UUID, comment='Quext Customer UUID')
    community_id = Column(UUID, comment='Quext Community UUID')
    external_id = Column(String, comment='External Id Reference')
    lease_id = Column(ForeignKey('mdm.lease.lease_id'), comment='LeaseUUID from lease table')
    start_date = Column(Date, comment='Lease Interval Start Date')
    end_date = Column(Date, comment='Lease Interval End Date')
    lease_interval_type_name = Column(String, comment='Lease Interval Type')
    lease_interval_name = Column(String, comment='Lease Interval Name')
    lease_interval_status = Column(String, comment='Lease Interval Status')
    lease_approved_on = Column(Date, comment='Lease Approved on date')
    application_completed_on = Column(Date, comment='Application Completed on Date')
    external_application_id = Column(String, comment='External Application Id reference')
    created_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record created timestamp')
    updated_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record updated timestamp')

    lease = relationship('Lease')


class RentableItem(Base):
    __tablename__ = 'rentable_item'
    __table_args__ = {'schema': 'mdm'}

    rentable_item_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"), comment='Rentable Item Record Identifier')
    customer_id = Column(UUID, comment='Quext Customer UUID')
    community_id = Column(UUID, comment='Quext Community UUID')
    external_id = Column(String, comment='External Id reference')
    lease_id = Column(ForeignKey('mdm.lease.lease_id'), comment='Lease UUID from lease table')
    item_type = Column(String, comment='Rentable Item type')
    type_category = Column(String, comment='Rentable Item Category')
    type_group = Column(String, comment='Rentable item category')
    type_name = Column(String, comment='Rentable Item name')
    lease_status_type = Column(String, comment='Rentable item status')
    start_date = Column(Date, comment='Start date of rentable item')
    end_date = Column(Date, comment='End date of rentable item')
    agent_id = Column(String, comment='Agent Id for rentable item')
    created_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record created timestamp')
    updated_date = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='Record updated timestamp')

    lease = relationship('Lease')    


class CommunityPartnerKeyValues(Base):
    # community_uuid, partner_name, partner_name (primary)
    __tablename__ = 'community_partner_key_values'
    __table_args__ = {'schema': 'public'}

    community_uuid = Column(UUID, primary_key=True, nullable=False)
    created_at = Column(DateTime(True), nullable=True)
    updated_at = Column(DateTime(True), nullable=True)
    partner_name = Column(String, primary_key=True, nullable=False)
    key_name = Column(String, primary_key=True, nullable=False)
    key_value = Column(String, nullable=False)

class PartnerSecurity(Base):
    # partner_uuid (primary)
    __tablename__ = 'partner_security'
    __table_args__ = {'schema': 'public'}

    partner_uuid = Column(UUID, primary_key=True)
    created_at = Column(DateTime(True), nullable=False)
    updated_at = Column(DateTime(True), nullable=False)
    user = Column(Integer)
    security = Column(JSONB, nullable=False)
    id = Column(Integer)

class Communities(Base):
    # community_uuid (primary)
    __tablename__ = 'communities'
    __table_args__ = {'schema': 'public'}
    
    created_at = Column(DateTime(True), nullable=True)
    updated_at = Column(DateTime(True), nullable=True)
    customer_uuid = Column(UUID, nullable=False)
    deleted_at = Column(DateTime(True), nullable=True)
    community_uuid = Column(UUID, primary_key=True, nullable=False)
    address_line_2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    mailing_address_line_1 = Column(String, nullable=True)
    mailing_address_line_2 = Column(String, nullable=True)
    mailing_city = Column(String, nullable=True)
    mailing_state = Column(String, nullable=True)
    mailing_postal_code = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    website_url = Column(String, nullable=True)
    timezone_id = Column(String, nullable=True)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    owner = Column(String, nullable=True)
    address_line_1 = Column(String, nullable=True)

class CommunityPurposePartners(Base):
    # community_uuid, purpose_name (primary)
    __tablename__ = 'community_purpose_partners'
    __table_args__ = {'schema': 'public'}

    community_uuid = Column(UUID, primary_key=True, nullable=False)
    created_at = Column(DateTime(True), nullable=True)
    updated_at = Column(DateTime(True), nullable=True)
    purpose_name = Column(String, primary_key=True, nullable=False)
    partner_name = Column(String, nullable=False)
	
class Partners(Base): 
    # partner_name(primary), partner_uuid (unique)
    __tablename__ = 'partners'
    __table_args__ = {'schema': 'public'}
    
    partner_uuid = Column(UUID, unique=True, nullable=False)
    created_at	= Column(DateTime(True), nullable=True)
    updated_at = Column(DateTime(True), nullable=True)
    partner_name = Column(String, primary_key=True, nullable=False)
    logo_url = Column(String, nullable=True)
