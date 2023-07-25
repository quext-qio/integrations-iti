from enum import Enum


class LeaseTerms:

    def __init__(self):
        self.lease_begin_date = ''
        self.lease_end_date = ''
        self.days_prorated = ''
        self.prorated_rent = ''
        self.prorated_rent_per_day = ''
        self.prorated_rent_due_date = ''
        self.prorated_rent_due_first_month = ''
        self.reletting_charge = ''
        self.reletting_charge_percent = ''
        self.rent = ''
        self.security_deposit = ''
        self.security_deposit_includes_animal_deposit = ''


class ResidentInformation:

    def __init__(self):
        self.resident = []
        self.occupant = []


class SecurityDeposit:

    def __init__(self):
        self.security_deposit_refund_check_payable = ''
        self.security_deposit_refund_one_check_mailed_to = ''


class LeaseData:

    def __init__(self):
        self.address = ''
        self.date_of_lease = ''
        self.unit_number = ''
        self.resident_information = {}
        self.maximum_guest_stay = ''
        self.lease_terms = {}
        self.security_deposit = {}


class StudentLease:

    def __init__(self):
        self.unit_number = ''
        self.bedroom_no = ''
        self.floor_plan = ''
        self.rent_for_term = ''
        self.payable_in = ''
        self.installments_of = ''
        self.bedroom_transfer_fee = ''
        self.unit_transfer_fee = ''
        self.special_provision = {}


class StudentSpecialProvision:

    def __init__(self):
        self.special_provision = ''


class OtherCharges:

    def __init__(self):
        self.automatic_renewal = ''
        self.additionalCharges = {}
        self.keys = {}
        self.insurance = {}


class AdditionalCharges:

    def __init__(self):
        self.charges_start = ''
        self.late_initial_charges = ''
        self.late_initial_charges_percentage = ''
        self.daily_late_charges = ''
        self.daily_late_charges_percentage = ''
        self.daily_late_charges_cannot_exceed = ''
        self.returned_check_charges = ''
        self.initial_pet_charge = ''
        self.daily_pet_charge = ''
        self.monthly_pest_control = ''
        self.monthly_trash_fee = ''


class Keys:

    def __init__(self):
        self.no_of_keys = ''
        self.no_of_mail_keys = ''
        self.no_of_other_access_key = ''
        self.unit_no = ''


class Insurance:

    def __init__(self):
        self.insurance = ''


class SpecialProvisionForms:

    def __init__(self):
        self.utility_paid_by_owner = {}
        self.special_provisions = {}
        self.unit_comes = {}
        self.pay_rent = {}
        self.notice_for_terminate_lease = {}


class UtilityPaidOwner:

    def __init__(self):
        self.gas = ''
        self.water = ''
        self.waste_water = ''
        self.electricity = ''
        self.trash = ''
        self.cable = ''
        self.master_antenna = ''
        self.internet = ''
        self.storm_water = ''
        self.government_fees = ''
        self.other_fees = ''
        self.electricity_bill = ''


class SpecialForms:

    def __init__(self):
        self.special_provisions = ''


class UnitComes:

    def __init__(self):
        self.unit_come = ''


class PayRent:

    def __init__(self):
        self.pay_on_site = ''
        self.pay_on_online = ''
        self.pay_on_website = ''


class TerminateLease:

    def __init__(self):
        self.terminate_lease_notice = ''


class AttachmentForm:

    def __init__(self):
        self.owner_representative = {}
        self.locator_service = {}
        self.copies_and_attachments = {}


class OwnerRepresentative:

    def __init__(self):
        self.address = ''
        self.telephone = ''
        self.fax = ''
        self.after_hours_phone = ''


class LocateService:

    def __init__(self):
        self.address = ''
        self.zip_code = ''
        self.name = ''
        self.phone = ''


class AttachmentCopies:

    def __init__(self):
        self.access_gates = ''
        self.special_provisions = ''
        self.utility_allocation = {}
        self.animal_addendum = ''
        self.apartment_rules = ''
        self.asbestos = ''
        self.bed_bug = ''
        self.early_termination = ''
        self.enclosed_garage = ''
        self.intrusion_alarm = ''
        self.inventory_and_condition = ''
        self.hazard_disclosure = ''
        self.contract_guaranty = ''
        self.housing = ''
        self.description = ''
        self.military_addendum = ''
        self.mold = ''
        self.cleaning_instructions = ''
        self.notice_of_move = ''
        self.parking_permit_quantity = ''
        self.parking_permit = ''
        self.rent_concession = ''
        self.renters_insurance = ''
        self.repair_request = ''
        self.dish = ''
        self.guidelines = ''
        self.tenant_guide = ''
        self.utility_submetering = {}
        self.other = []
        self.other_description = []


class UnitSubmetering:

    def __init__(self):
        self.electricity = ''
        self.gas = ''
        self.water = ''


class UtilityAllocations:

    def __init__(self):
        self.gas = ''
        self.electricity = ''
        self.cable_tv = ''
        self.utility_trash = ''
        self.water = ''
        self.central_system_costs = ''
        self.stormwater_drainage = ''
        self.govt_fees = ''


class AnimalAddendum:

    def __init__(self):
        self.additional_charges = {}
        self.information = {}
        self.special_provisions = {}
        self.emergency = {}
        self.pet_rules = {}


class AdditionalPetCharges:

    def __init__(self):
        self.security_deposite = ''
        self.monthly_rent = ''
        self.pet_fees = ''


class PetInformation:

    def __init__(self):
        self.name = []
        self.type = []
        self.breed = []
        self.color = []
        self.weight = []
        self.age = []
        self.city_license = []
        self.license_no = []
        self.last_rabies_shot = []
        self.housebroken = []
        self.pet_owner = []


class SpecialProvision:

    def __init__(self):
        self.special_provision = ''


class Emergence:

    def __init__(self):
        self.doctor_name = ''
        self.address = ''
        self.city = ''
        self.phone = ''


class PetRules:

    def __init__(self):
        self.pet_inside = ''
        self.pet_outside = ''


class EarlyLeaseTearm:

    def __init__(self):
        self.terminate_lease_last_day = ''
        self.lease_terminate = ''
        self.lease_terminate_fee = ''
        self.lease_terminate_notice_day = ''
        self.right_of_termination = ''
        self.lease_special_provision = {}


class EarlySpecialProvision:

    def __init__(self):
        self.special_provision = ''


class AllocationAddenda:

    def __init__(self):
        self.national_gas_addendum = {}
        self.government_fee_addendum = {}
        self.storm_water_addendum = {}
        self.trash_removal_addendum = {}
        self.central_system_allocations = {}


class NaturalGasAddendum:

    def __init__(self):
        self.gas_allocation_fee = ''
        self.gas_allocation_formula = ''
        self.gas_allocation_duration = ''
        self.gas_allocation_administrative_fee = ''


class GovernmentFeeAddendum:

    def __init__(self):
        self.cable_satelite = ''
        self.stormwater_drainage = ''
        self.addendum_trash = ''
        self.street_repair = ''
        self.emergency_services = ''
        self.conservation_district = ''
        self.inspection = ''
        self.registration_license = ''
        self.other = []
        self.other_desc = []
        self.late_fee = ''
        self.bill_based_on = ''
        self.administrative_fee = ''


class StormWaterAddendum:

    def __init__(self):
        self.bill_based_on = ''
        self.administrative_fee = ''


class TrashRemovalAddendum:

    def __init__(self):
        self.bill_based_on = ''
        self.administrative_fee = ''
        self.late_fee = ''


class CentralSystemAllocation:

    def __init__(self):
        self.allocate_basis = ''
        self.combo_formula = ''
        self.formula = ''
        self.heat_ac = ''
        self.hot_water = ''
        self.avg_basis = ''
        self.water_avg_basis = ''
        self.avg_hvac = ''
        self.sub_metered_formula = ''


class MicAddenda:

    def __init__(self):
        self.electronic_payment = {}
        self.enclosed_garage = {}
        self.legal_description = {}
        self.move_out_notice = {}
        self.no_smoking = {}
        self.patio_yard_maintenance = {}
        self.dish = {}
        self.trash_recycle = {}
        self.carrying_handguns = {}
        self.short_term_lease = {}
        self.install_dryer = {}


class ElectronicPayment:

    def __init__(self):
        self.resident = {}
        self.resident_rent = []
        self.special_provision = ''


class EnclosedGarage:

    def __init__(self):
        self.carport_provided = ''
        self.garage_space_no = ''
        self.carport_space_no = ''
        self.storage_unit_no = ''
        self.opener_fine = ''
        self.garage_key = ''
        self.garage_opener = ''
        self.carport_provided = ''
        self.garage_provided = ''


class LegalDescription:

    def __init__(self):
        self.description = ''


class MoveOUtNotice:

    def __init__(self):
        self.notice_for_move_out = ''


class NoSmoking:

    def __init__(self):
        self.permitted_balcony = ''
        self.permitted_outside = ''
        self.smoking_areas = ''
        self.smoking_distance = ''


class PatioMaintenance:

    def __init__(self):
        self.mowing = ''
        self.watering = ''
        self.trash = ''
        self.fertilize = ''


class Dish:

    def __init__(self):
        self.no_dishes = ''
        self.insurance = ''
        self.security_deposit = ''
        self.security_deposit_days = ''


class TrashRecycle:

    def __init__(self):
        self.bill_late_fee = ''
        self.recycling_flat_fee = ''
        self.administrative_fee_flat = ''


class CarryingHandguns:

    def __init__(self):
        self.conceal_area = ''
        self.office = ''
        self.property = ''
        self.rooms = ''
        self.open_carry_area = ''
        self.open_carry_office = ''
        self.open_carry_property = ''
        self.open_carry_rooms = ''


class ShorLease:

    def __init__(self):
        self.special_provisions = ''


class InstallDryer:

    def __init__(self):
        self.dryer = ''
        self.washer = ''


class RemoteCard:

    def __init__(self):
        self.remote_control_code = {}
        self.remote_control_lust_damaged = {}


class RemoteCardAccess:

    def __init__(self):
        self.gate_access = ''
        self.add_card_fee = ''
        self.card = ''
        self.add_remote_fee = ''
        self.code = ''


class RemoteLustCard:

    def __init__(self):
        self.lost_remote = ''
        self.replace_remote_fee = ''
        self.lost_remote_deduct = ''
        self.addendum_lost_card = ''
        self.replace_card_fee = ''
        self.lost_card_deduct = ''
        self.addendum_code_change = ''


class ElectricWaterWasteWater:

    def __init__(self):
        self.electric_allocation_bill = {}
        self.water_wasteWater = {}


class WaterWasteWater:

    def __init__(self):
        self.average_monthly_bill = ''
        self.lowest_monthly_bill = ''
        self.highest_monthly_bill = ''
        self.service_fee = ''
        self.from_date = ''
        self.to_date = ''
        self.bill_date = ''
        self.method = ''


class ElectricAllocationBill:

    def __init__(self):
        self.reconnect_fee = ''
        self.metering = ''
        self.square_feet_percent = ''
        self.estimated_percent_use = ''
        self.electric_method = ''


class RentConcessions:

    def __init__(self):
        self.concession_one_time = ''
        self.one_time_amount = ''
        self.one_time_months = ''
        self.special_provisions = ''
        self.monthly_discount = ''
        self.discounted_months = ''
        self.concession_amount = ''


class IntrusionAlarm:

    def __init__(self):
        self.alarm = ''
        self.required_to_activate = ''
        self.activation_contact = ''
        self.instructions_attached = ''
        self.required_company = ''
        self.resident_chooses_company = ''
        self.repair_contact = ''
        self.paid_by = ''
        self.required_to_activate = ''
        self.maintainer = ''


class AdditionalProvisions:

    def __init__(self):
        self.provisions = {}
        self.rental_dwelling = {}
        self.activities = {}


class AdditionalSpecialProvisions:

    def __init__(self):
        self.special_provision = ''


class RentalDwelling:

    def __init__(self):
        self.bedroom_sharing = ''
        self.sharing_common_areas = ''
        self.transfer_fee = ''


class ActivitiesAddendum:

    def __init__(self):
        self.construction_provisions = ''


class RenterInsurance:

    def __init__(self):
        self.liability_limit = ''
        self.insurance_default_fee = ''


class LeaseGuaranty:

    def __init__(self):
        self.date_for_renewal = ''
        self.obligations = ''
        self.contract = {}


class ContractGauranty:

    def __init__(self):
        self.contract_guaranty = ''


class SummaryKeyInformation:

    def __init__(self):
        self.summary_information = {}


class SummaryInformation:

    def __init__(self):
        self.address = ''
        self.unit_number = ''
        self.start_date = ''
        self.end_date = ''
        self.lease_termination = ''
        self.prorated = ''
        self.security_deposit = ''
        self.animal_deposit = ''
        self.refund_check_payable = ''
        self.check_mailed_to = ''
        self.apartment_keys = ''
        self.mail_keys = ''
        self.other_keys = ''
        self.rent_concession = ''
        self.pay_rent = ''
        self.online_site = ''
        self.on_site = ''
        self.garage_in_rent = ''
        self.carport_in_rent = ''
        self.other_cost_in_rent = ''
        self.storage_in_rent = ''
        self.washer_dryer_in_rent = ''
        self.gas = ''
        self.water = ''
        self.trash = ''
        self.electricity = ''
        self.cable_tv = ''
        self.master_antenna = ''
        self.internet = ''
        self.drainage = ''
        self.other = ''
        self.insurance_requirement = ''
        self.due_date = ''
        self.prorated = ''
        self.rent_amount = ''
        self.initial_charge = ''
        self.percentage_of_rent = ''
        self.daily_charge = ''
        self.daily_percent_of_rent = ''
        self.check_charge = ''
        self.additional_rent = ''
        self.pet_initial_charge = ''
        self.pet_daily_charge = ''
        self.monthly_pest_rent = ''
        self.monthly_trash_rent = ''
        self.electric_transfer_fee = ''
        self.provisions = ''


class Covid19:

    def __init__(self):
        self.notice_for_temporary_waiver = {}
        self.payment_plan_agreement = {}
        self.virus_warning_and_waiver = {}


class WaiverNotice:

    def __init__(self):
        self.begin_date = ''
        self.end_date = ''
        self.rent_due_date = ''
        self.phone_no = ''
        self.email_id = ''


class PaymentAgreement:

    def __init__(self):
        self.date = ''
        self.year = ''
        self.current_month = ''
        self.next_month = ''
        self.due_time_period = ''
        self.due_description = ''
        self.due_date = []
        self.amount = []


class VirusWarningWaiver:

    def __init__(self):
        self.waiver_signed_date = ''
        self.waiver_signed_year = ''


class LeadHazard:

    def __init__(self):
        self.paint_knowledge = ''
        self.knowledge_comments = ''
        self.paint_reports = ''
        self.reports_comment = ''


class BaseLeaseResponse:

    def __init__(self):
        self.lease_id = ''
        self.property_id = ''
        self.created_at = ''
        self.updated_at = ''
        self.renewed = ''
        self.printed = ''
        self.renewal_printed = ''
        self.editable = ''
        self.lease_terms = {}
        self.student_lease = {}
        self.other_lease = {}
        self.special_provisions = {}
        self.attachment = {}
        self.animal_addendum = {}
        self.lead_hazard = {}
        self.early_terms = {}
        self.allocation_addenda = {}
        self.mic_addenda = {}
        self.remote_card = {}
        self.electricity_water_waste_water = {}
        self.concessions = {}
        self.intrusion_alarm = {}
        self.additional_provision = {}
        self.rent_insurance = {}
        self.lease_guaranty = {}
        self.summary_key_information = {}
        self.covid_details = {}
        self.custom = {}


class ErrorType(Enum):
    NONE = ''
    VALIDATION_ERROR = 'ValidationError'
    SYSTEM_ERROR = 'SystemError'
    AUTHORIZATION_ERROR = 'AuthorizationError'


class BaseError:

    def __init__(self):
        self.errorType = ''
        self.errorMessages = {}


class BaseResponse:

    def __init__(self):
        self.data = {}
        self.error = {}
