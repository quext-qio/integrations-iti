from collections import defaultdict
from typing import List


class CommunityAmenity:
    name: str
    type: str

    def __init__(self, name: str, type: str) -> None:
        self.name = name
        self.type = type


class ExternalIdentifier:
    referrer: str
    data_type: str
    value: str

    def __init__(self, referrer: str, data_type: str, value: str) -> None:
        self.referrer = referrer
        self.data_type = data_type
        self.value = value


class ContactMethods:
    phone: str
    fax: str
    speed_dial: str
    email: str

    def __init__(self, phone: str, fax: str, speed_dial: str, email: str):
        self.phone = phone
        self.fax = fax
        self.speed_dial = speed_dial
        self.email = email


class GpsLocation:
    lat: str
    lon: str

    def __init__(self, lat: str, lon: str) -> None:
        self.lat = lat
        self.lon = lon


class PhysicalLocation:
    address: str
    address2: str
    city: str
    state: str
    postal_code: str

    def __init__(self, address: str, address2: str, city: str, state: str, postal_code: str) -> None:
        self.address = address
        self.address2 = address2
        self.city = city
        self.state = state
        self.postal_code = postal_code


class Layout:
    layout_image: str
    layout_type: str

    def __init__(self, layout_image: str, layout_type: str):
        self.layout_image = layout_image
        self.layout_type = layout_type


class FloorPlan:
    name: str
    floor_plan_id: str
    floor_plan_image: str
    virtual_tour_url: str

    def __init__(self, name: str, floor_plan_id: str, floor_plan_image: str, virtual_tour_url: str):
        self.name = name
        self.floor_plan_id = floor_plan_id
        self.floor_plan_image = floor_plan_image
        self.virtual_tour_url = virtual_tour_url


class Place:
    place: str

    def __init__(self, place: str):
        self.place = place


class Space:
    quext_space_id: str
    place: List[Place]
    min_sqft: int
    max_sqft: int
    level_of_primary_entry: str
    layout: Layout

    def __init__(self, quext_space_id: str, place: List[Place], min_sqft: int, max_sqft: int,
                 level_of_primary_entry: str,
                 layout: Layout = None):
        self.quext_space_id: quext_space_id
        self.place = place
        self.min_sqft = min_sqft
        self.max_sqft = max_sqft
        self.level_of_primary_entry = level_of_primary_entry
        self.layout = layout


class Structure:
    space: List[Space]

    def __init__(self, space: List[Space]):
        self.space = space


class Property:
    physical_location: PhysicalLocation
    gpslocation: GpsLocation
    structure: List[Structure]
    country: str

    def __init__(self, country: str, structure: List[Structure], physical_location: PhysicalLocation = None,
                 gpsLocation: GpsLocation = None) -> None:
        self.physical_location = physical_location
        self.gpsLocation = gpsLocation
        self.structure = structure
        self.country = country


class Amenity:
    amenity_id: str
    amenity_description: str
    added_rent_value: str
    valid_starting: str
    valid_through: str

    def __init__(self, amenity_id: str, amenity_description: str, added_rent_value: str, valid_starting: str,
                 valid_through: str):
        self.amenity_id = amenity_id
        self.amenity_description = amenity_description
        self.added_rent_value = added_rent_value
        self.valid_starting = valid_starting
        self.valid_through = valid_through


class ResidentialSpace(Space):
    bedrooms: int
    full_bathrooms: int
    half_bathrooms: int
    floor_plan: FloorPlan

    def __init__(self, bedrooms: int, full_bathrooms: int, half_bathrooms: int, space_id: str,
                 place: List[Place], min_sqft: int, max_sqft: int,
                 level_of_primary_entry: str, floor_plan: FloorPlan = None, layout: Layout = None):
        super().__init__(space_id, place, min_sqft, max_sqft, level_of_primary_entry, layout)
        self.bedrooms = bedrooms
        self.full_bathrooms = full_bathrooms
        self.half_bathrooms = half_bathrooms
        self.floor_plan = floor_plan


class Event:
    type: str
    vacate_date: str

    def __init__(self, type: str, vacate_date: str):
        self.type = type
        self.vacate_date = vacate_date


class CustomerEvent:
    type: str
    id: str
    date: str
    created_at: str
    person_id: int

    def __init__(self, type: str, id: str, date: str, created_at: str, person_id: int):
        self.type = type
        self.id = id
        self.date = date
        self.created_at = created_at
        self.person_id = person_id


class Person:
    first_name: str
    last_name: str
    ssn: str
    date_of_birth: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    postal: str
    desired_move_in_date: str
    desired_move_out_date: str
    desired_bed_rooms: int
    additional_occupants: int
    pets: str

    def __init__(self, first_name: str, last_name: str, ssn: str, date_of_birth: str, email: str, phone: str,
                 address: str, city: str, state: str, postal: str, desired_move_in_date: str,
                 desired_move_out_date: str,
                 desired_bed_rooms: int, additional_occupants: int, pets: str):
        self.first_name = first_name
        self.last_name = last_name
        self.ssn = ssn
        self.date_of_birth = date_of_birth
        self.email = email
        self.phone = phone
        self.address = address
        self.city = city
        self.state = state
        self.postal = postal
        self.desired_move_in_date = desired_move_in_date
        self.desired_move_out_date = desired_move_out_date
        self.desired_bed_rooms = desired_bed_rooms
        self.additional_occupants = additional_occupants
        self.pets = pets


class Resident(Person):
    resident_id: int
    prospect_id: int
    resident_type: str
    actual_move_in_date: str
    notice_date: str
    estimated_move_out_date: str
    actual_move_out_date: str

    def __init__(self, first_name: str, last_name: str, ssn: str, date_of_birth: str, email: str, phone: str,
                 address: str, city: str, state: str, postal: str, desired_move_in_date: str,
                 desired_move_out_date: str, desired_bed_rooms: int, additional_occupants: int, pets: str,
                 resident_id: int, prospect_id: int, resident_type: str,
                 actual_move_in_date: str, notice_date: str, estimated_move_out_date: str, actual_move_out_date: str):
        super().__init__(first_name, last_name, ssn, date_of_birth, email, phone, address, city, state, postal,
                         desired_move_in_date, desired_move_out_date, desired_bed_rooms, additional_occupants, pets)
        self.resident_id = resident_id
        self.prospect_id = prospect_id
        self.resident_type = resident_type
        self.actual_move_in_date = actual_move_in_date
        self.notice_date = notice_date
        self.estimated_move_out_date = estimated_move_out_date
        self.actual_move_out_date = actual_move_out_date


class TransactionCode:
    charge_code_id: str
    charge_code_name: str

    def __init__(self, charge_code_id: str, charge_code_name: str):
        self.charge_code_id = charge_code_id
        self.charge_code_name = charge_code_name


class MarketRent:
    market_rent_amount: str
    valid_beginning_at: str
    valid_ending_at: str

    def __init__(self, market_rent_amount: str, valid_beginning_at: str, valid_ending_at: str):
        self.market_rent_amount = market_rent_amount
        self.valid_beginning_at = valid_beginning_at
        self.valid_ending_at = valid_ending_at


class LeaseTransaction:
    transaction_id: str
    transaction_posted_date: str
    transaction_due_date: str
    transaction_charge_code_id: str
    transaction_charge_code_name: str
    transaction_amount: str
    transaction_override_amount: str
    transaction_type: str
    transaction_notes: str
    transaction_isPaid: bool

    def __init__(self, transaction_id: str, transaction_posted_date: str, transaction_due_date: str,
                 transaction_charge_code_id: str, transaction_charge_code_name: str, transaction_amount: str,
                 transaction_override_amount: str,
                 transaction_type: str, transaction_notes: str, _isPaid=False):
        self.transaction_id = transaction_id
        self.transaction_posted_date = transaction_posted_date
        self.transaction_due_date = transaction_due_date
        self.transaction_charge_code_id = transaction_charge_code_id
        self.transaction_charge_code_name = transaction_charge_code_name
        self.transaction_amount = transaction_amount
        self.transaction_override_amount = transaction_override_amount
        self.transaction_type = transaction_type
        self.transaction_notes = transaction_notes
        self.transaction_isPaid = _isPaid


class Lease:
    lease_id: int
    lease_start_date: str
    lease_end_date: str
    is_lease_active: int
    actual_rent_amount: str
    market_rent: MarketRent
    lease_transaction: List[LeaseTransaction]
    residents: List[Resident]

    def __init__(self, lease_id: int, lease_start_date: str, lease_end_date: str, is_lease_active: int,
                 actual_rent_amount: str, resident: List[Resident] = None, market_rent: MarketRent = None,
                 lease_transaction: List[LeaseTransaction] = None):
        self.lease_id = lease_id
        self.lease_start_date = lease_start_date
        self.lease_end_date = lease_end_date
        self.is_lease_active = is_lease_active
        self.actual_rent_amount = actual_rent_amount
        self.residents = []
        self.market_rent = market_rent
        self.lease_transaction = []


class Unit:
    name: str
    residential_space: ResidentialSpace
    status: List[str]
    availability: str
    price: float
    market_rent: float
    rent_amount: float
    occupancy_status: str
    leasable: int
    event: Event
    valid_starting: str
    available_date: str
    unit_amenities: List[Amenity]
    external_identifier: List[ExternalIdentifier]
    lease: Lease

    def __init__(self, name: str, residential_space: ResidentialSpace, status: List[str], availability: str,
                 price: float, market_rent: float, rent_amount: float, occupancy_status: str, valid_starting: str,
                 available_date: str,
                 leasable: int, event: Event = None, lease: Lease = None, _amenities: List[Amenity] = None,
                 external_identifier: List[ExternalIdentifier] = None) -> None:
        self.name = name
        self.residential_space = residential_space
        self.status = status
        self.availability = availability
        self.price = price
        self.market_rent = market_rent
        self.rent_amount = rent_amount
        self.occupancy_status = occupancy_status
        self.leasable = leasable
        self.event = event
        self.valid_starting = valid_starting
        self.available_date = available_date
        self.lease = lease
        self.unit_amenities = []
        self.external_identifier = external_identifier


class Accounting:
    transaction_codes: List[TransactionCode]

    def __init__(self):
        self.transaction_codes = []


class Community:
    short_name: str
    legal_name: str
    quext_id: str
    status: str
    unit_count: int
    external_identifier: List[ExternalIdentifier]
    property: Property
    community_amenities: List[CommunityAmenity]
    contact_methods: ContactMethods
    units: {}
    people: List[Resident]
    leases: {}
    accounting: Accounting
    lease_transaction: List[LeaseTransaction]
    events: List[CustomerEvent]

    def __init__(self, short_name: str, legal_name: str, quext_id: str, status: str, unit_count: int,
                 property: Property,
                 community_amenities: List[CommunityAmenity], contact_methods: ContactMethods,
                 external_identifier: List[ExternalIdentifier] = None, units: {} = None, people: List[Resident] = None,
                 leases: {} = None,
                 accounting: Accounting = None, lease_transaction: List[LeaseTransaction] = None,
                 events: List[CustomerEvent] = None) -> None:
        self.short_name = short_name
        self.legal_name = legal_name
        self.quext_id = quext_id
        self.status = status
        self.unit_count = unit_count
        self.external_identifier = external_identifier
        self.property = property
        self.community_amenities = community_amenities
        self.contact_methods = contact_methods
        self.units = {}
        self.people = []
        self.leases = leases
        self.accounting = accounting
        self.lease_transaction = []
        self.events = []


class Data:
    community: {}

    def __init__(self, community: {}) -> None:
        self.community = defaultdict(Community)


class CommonStructure:
    source: str
    format: str
    date: str
    action: str
    data: Data

    def __init__(self, source: str, format: str, date: str, action: str, data: Data) -> None:
        self.source = source
        self.format = format
        self.date = date
        self.action = action
        self.data = data
