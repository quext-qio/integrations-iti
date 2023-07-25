import json
import logging
from datetime import datetime

import jwt

from LeaseManagementShared.Models.BlueMoon import BlueMoonLease
from LeaseManagementShared.Models.BlueMoonLeaseResponse import BaseResponse, BaseError, ErrorType
from LeaseManagementShared.Models import BlueMoonLeaseResponse
from LeaseManagementShared.Utilities.BlueMoonConstants import BlueMoonConstants
from LeaseManagementShared.Utilities.Convert import Convert
from LeaseManagementShared.Utilities.DataValidation import Validate, Schema, PlatformData
from LeaseManagementShared.Utilities.HTTPHelper import sendRequest, HTTPRequest
from LeaseManagementShared.Utilities.LeaseIntegrationConstants import LeaseIntegrationConstants
from LeaseManagementShared.Utilities.LeaseIntegrationInterface import PlatformInterface


def keys_exists(element, *keys):
    '''
    Check if *keys (nested) exists in `element` (dict).
    '''
    if not isinstance(element, dict):
        raise AttributeError('keys_exists() expects dict as first argument.')
    if len(keys) == 0:
        raise AttributeError('keys_exists() expects at least two arguments, one given.')

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True


def nestedDictIterator(dict_obj):
    ''' This function accepts a nested dictionary as argument
        and iterate over all values of nested dictionaries
    '''
    # Iterate over all key-value pairs of dict argument
    for key, value in dict_obj.items():
        if key != 'custom_forms':

            # Check if value is of dict type
            if isinstance(value, dict):
                # If value is dict then iterate over all its values
                for pair in nestedDictIterator(value):
                    yield [key, *pair]
            else:
                # If value is not dict type then yield the value
                if isinstance(value, list):
                    for item in range(len(value)):
                        yield [key + '_' + str(item + 1), value[item]]
                else:
                    yield [key, value]


class BLUEMOON(PlatformInterface):

    def createLeaseRequestData(self, leaseData: dict, platformData: dict, tokenData: dict, paramsData: dict = None):
        platformData = platformData['platformData']
        _body, _header, _param, _error = {}, {}, {}, {}
        isValid, _error = Validate.schema(Schema.CREATE_LEASE, leaseData)
        # headers
        _header = {BlueMoonConstants.AUTHORIZATION: BlueMoonConstants.TOKEN_BEARER.format(tokenData['access_token'])}
        if isValid:
            _body = BlueMoonLease(platformData[BlueMoonConstants.PROPERTY_ID])

            # adding standard and custom forms dictionaries for bluemoon payload
            _body.standard = {}
            _body.custom = {}

            for pair in nestedDictIterator(leaseData):
                _body.standard[pair[-2]] = pair[-1]
            if 'custom_forms' in leaseData:
                _body.custom = leaseData["custom_forms"]
            if paramsData and 'leaseId' in paramsData:
                _param['id'] = paramsData['leaseId']
            else:
                _param['id'] = ''

        return _body, _header, _param, _error

    def updateLeaseRequestData(self, leaseData: dict, platformData: dict, tokenData: dict, paramsData: dict):
        # utilizing the createLeaseRequestData method, as bluemoon have same payload for both creating and
        # updating lease
        _body, _header, _param, _error = self.createLeaseRequestData(leaseData, platformData, tokenData, paramsData)

        return _body, _header, _param, _error

    def deleteLeaseRequestData(self, platformData: dict, tokenData: dict, paramsData: dict):
        _header, _param, _error = {}, {}, {}
        if LeaseIntegrationConstants.LEASE_ID in paramsData and paramsData[LeaseIntegrationConstants.LEASE_ID] != '':
            _param[LeaseIntegrationConstants.LEASE_ID] = paramsData[LeaseIntegrationConstants.LEASE_ID]
        else:
            _header = {
                BlueMoonConstants.AUTHORIZATION: BlueMoonConstants.TOKEN_BEARER.format(tokenData['access_token'])
            }
        isValid, _error = Validate.schema(Schema.DELETE_LEASE, _param)
        if isValid:
            _header = {BlueMoonConstants.AUTHORIZATION: BlueMoonConstants.TOKEN_BEARER.format(tokenData['access_token'])}

        return _header, _param, _error

    def getLeaseRequestData(self, platformData: dict, tokenData: dict, paramsData: dict):
        _header, _param, _error = {}, {}, {}
        _header, _param, _error = self.deleteLeaseRequestData(platformData, tokenData, paramsData)

        return _header, _param, _error

    def getAuthorizationData(self, platformData: dict, _cacheData: dict = None):
        setCache = False
        if _cacheData is None:
            setCache = True

            authData = {'username': platformData['username'],
                        'password': platformData['password'],
                        'grant_type': 'password',
                        "scope": ["full"],
                        'client_id': platformData['client_id'],
                        'client_secret': platformData['client_secret']}
            tokenData = sendRequest(HTTPRequest.POST, BlueMoonConstants.URL, Convert.toJson(authData), '',
                                    LeaseIntegrationConstants.HEADERS)
            return setCache, json.loads(tokenData.text)
        else:
            if BLUEMOON.isExpired(_cacheData):
                setCache = True
                refreshTokenData = BLUEMOON.refreshAuthorizationData(platformData, _cacheData)

                tokenData = sendRequest(HTTPRequest.POST, BlueMoonConstants.URL,
                                        Convert.toJson(refreshTokenData), '',
                                        LeaseIntegrationConstants.HEADERS)
                return setCache, json.loads(tokenData.text)
            else:
                return setCache, _cacheData

    @staticmethod
    def isExpired(data: dict):
        token = data['access_token']
        jwtData = jwt.decode(token, verify=False)
        days = datetime.now() - datetime.utcfromtimestamp(jwtData['iat'])
        if days.days < 12:
            return False
        return True

    @staticmethod
    def refreshAuthorizationData(_authorizationData: dict, _tokenData: dict):
        refreshTokenData = {
            'client_id': _authorizationData['client_id'],
            'client_secret': _authorizationData['client_secret'],
            'grant_type': 'refresh_token',
            'refresh_token': _tokenData['refresh_token']
        }
        return refreshTokenData

    def formatCreateLeaseResponseData(self, _responseData: dict):
        response = BaseResponse()
        response.error = BaseError()
        responseCode = _responseData['responseCode']
        responseData = _responseData['responseMessage']
        if responseCode == 201:
            # Creating a  Lease for a specific property
            leaseResponse = BlueMoonLeaseResponse.BaseLeaseResponse()
            leaseResponse.lease_id = responseData['id']
            leaseResponse.property_id = responseData['property_id']
            leaseResponse.created_at = responseData['created_at']
            leaseResponse.updated_at = responseData['updated_at']
            leaseResponse.renewed = responseData['renewed']
            leaseResponse.printed = responseData['printed']
            leaseResponse.renewal_printed = responseData['renewal_printed']
            leaseResponse.editable = responseData['editable']

            # format resident information like residents and occupants of a list
            residentInformation = BlueMoonLeaseResponse.ResidentInformation()
            residentList, occupantList = [], []
            for i in range(1, 7):
                resident = 'resident' + '_' + str(i)
                residentList.append(responseData['standard'][resident])
            for i in range(1, 5):
                occupant = 'occupant' + '_' + str(i)
                occupantList.append(responseData['standard'][occupant])
            residentInformation.resident = residentList
            residentInformation.occupant = occupantList

            # format lease information such as rent and other deposits

            leaseTerms = BlueMoonLeaseResponse.LeaseTerms()
            leaseTerms.lease_begin_date = responseData['standard']['lease_begin_date']
            leaseTerms.lease_end_date = responseData['standard']['lease_end_date']
            leaseTerms.days_prorated = responseData['standard']['days_prorated']
            leaseTerms.prorated_rent = responseData['standard']['prorated_rent']
            leaseTerms.prorated_rent_per_day = responseData['standard'][
                'prorated_rent_per_day']
            leaseTerms.prorated_rent_due_date = responseData['standard'][
                'prorated_rent_due_date']
            leaseTerms.prorated_rent_due_first_month = responseData['standard'][
                'prorated_rent_due_first_month']
            leaseTerms.reletting_charge = responseData['standard']['reletting_charge']
            leaseTerms.reletting_charge_percent = responseData['standard']['reletting_charge_percent']
            leaseTerms.rent = responseData['standard']['rent']
            leaseTerms.security_deposit = responseData['standard']['security_deposit']
            leaseTerms.security_deposit_includes_animal_deposit = responseData['standard'][
                'security_deposit_includes_animal_deposit']

            # format refunds information
            securityDeposit = BlueMoonLeaseResponse.SecurityDeposit()
            securityDeposit.security_deposit_refund_check_payable = responseData['standard'][
                'security_deposit_refund_check_payable']
            securityDeposit.security_deposit_refund_one_check_mailed_to = responseData['standard'][
                'security_deposit_refund_one_check_mailed_to']

            #  create the lease specific information of the lease
            sectionLeaseTerms = BlueMoonLeaseResponse.LeaseData()
            sectionLeaseTerms.address = responseData['standard']['address']
            sectionLeaseTerms.date_of_lease = responseData['standard']['date_of_lease']
            sectionLeaseTerms.unit_number = responseData['standard']['unit_number']
            sectionLeaseTerms.residentInformation = residentInformation
            sectionLeaseTerms.maximum_guest_stay = responseData['standard']['maximum_guest_stay']
            sectionLeaseTerms.leaseTerms = leaseTerms
            sectionLeaseTerms.securityDeposit = securityDeposit

            # get special provision for student lease creation
            specialProvision = BlueMoonLeaseResponse.StudentSpecialProvision()
            specialProvision.special_provision = responseData['standard']['student_housing_special_provisions']

            # create student lease
            studentLease = BlueMoonLeaseResponse.StudentLease()
            studentLease.unit_number = responseData['standard']['unit_number']
            studentLease.bedroom_no = responseData['standard']['student_lease_bedroom_number']
            studentLease.floor_plan = responseData['standard']['student_lease_floor_plan']
            studentLease.rent_for_term = responseData['standard']['student_lease_total_lease_term_rent']
            studentLease.payable_in = responseData['standard']['student_lease_apartment']
            studentLease.installments_of = responseData['standard']['student_lease_monthly_installment']
            studentLease.bedroom_transfer_fee = responseData['standard']['student_lease_bedroom_change_transfer_fee']
            studentLease.unit_transfer_fee = responseData['standard']['student_lease_unit_transfer_fee']
            studentLease.special_provision = specialProvision

            # create other lease
            additionalCharge = BlueMoonLeaseResponse.AdditionalCharges()
            additionalCharge.charges_start = responseData['standard']['rent_due_date']
            additionalCharge.late_initial_charges = responseData['standard']['late_charge_initial_charge']
            additionalCharge.late_initial_charges_percentage = responseData['standard']['late_charge_percentage_of_rent']
            additionalCharge.daily_late_charges = responseData['standard']['late_charge_daily_charge']
            additionalCharge.daily_late_charges_percentage = responseData['standard']\
            ['late_charge_daily_percent_of_rent']
            additionalCharge.daily_late_charges_cannot_exceed = responseData['standard']\
            ['late_charge_daily_cannot_exceed_days']
            additionalCharge.returned_check_charges = responseData['standard']['returned_check_charge']
            additionalCharge.initial_pet_charge = responseData['standard']['pet_charge_initial_charge']
            additionalCharge.daily_pet_charge = responseData['standard']['pet_charge_daily_charge']
            additionalCharge.monthly_pest_control = responseData['standard']['monthly_pest_control_rent']
            additionalCharge.monthly_trash_fee = responseData['standard']['monthly_trash_rent']

            key = BlueMoonLeaseResponse.Keys()
            key.no_of_keys = responseData['standard']['number_of_other_keys']
            key.no_of_mail_keys = responseData['standard']['number_of_mail_keys']
            key.no_of_other_access_key = responseData['standard']['other_key_type']
            key.unit_no = responseData['standard']['old_unit_number']

            insurance = BlueMoonLeaseResponse.Insurance()
            insurance.insurance = responseData['standard']['renters_insurance_requirement']

            otherCharges = BlueMoonLeaseResponse.OtherCharges()
            otherCharges.automatic_renewal = responseData['standard']['days_required_for_notice_of_lease_termination']
            otherCharges.additionalCharges = additionalCharge
            otherCharges.keys = key
            otherCharges.insurance = insurance

            # special provision form create
            leaseTormination = BlueMoonLeaseResponse.TerminateLease()
            leaseTormination.terminate_lease_notice = responseData['standard']['lease_terminates_last_day_of_month']

            leaseRentPay = BlueMoonLeaseResponse.PayRent()
            leaseRentPay.pay_on_site = responseData['standard']['pay_rent_on_site']
            leaseRentPay.pay_on_online = responseData['standard']['pay_rent_at_online_site']
            leaseRentPay.pay_on_website = responseData['standard']['pay_rent_address']

            specialUnits = BlueMoonLeaseResponse.UnitComes()
            specialUnits.unit_come = responseData['standard']['unit_furnished']

            leaseForms = BlueMoonLeaseResponse.SpecialForms()
            leaseForms.special_provisions = responseData['standard']['special_provisions']

            ownerPaidLease = BlueMoonLeaseResponse.UtilityPaidOwner()
            ownerPaidLease.gas = responseData['standard']['utilities_gas']
            ownerPaidLease.water = responseData['standard']['utilities_water']
            ownerPaidLease.waste_water = responseData['standard']['utilities_wastewater']
            ownerPaidLease.electricity = responseData['standard']['utilities_electricity']
            ownerPaidLease.trash = responseData['standard']['utilities_trash']
            ownerPaidLease.cable = responseData['standard']['utilities_cable_tv']
            ownerPaidLease.master_antenna = responseData['standard']['utilities_master_antenna']
            ownerPaidLease.internet = responseData['standard']['utilities_internet']
            ownerPaidLease.storm_water = responseData['standard']['utilities_stormwater_drainage']
            ownerPaidLease.government_fees = responseData['standard']['utilities_government_fees']
            ownerPaidLease.other_fees = responseData['standard']['utilities_other']
            ownerPaidLease.electricity_bill = responseData['standard']['electric_transfer_fee']

            leaseSpecialProvisions = BlueMoonLeaseResponse.SpecialProvisionForms()
            leaseSpecialProvisions.utility_paid_by_owner = ownerPaidLease
            leaseSpecialProvisions.special_provisions = leaseForms
            leaseSpecialProvisions.pay_rent = leaseRentPay
            leaseSpecialProvisions.unit_comes = specialUnits
            leaseSpecialProvisions.notice_for_terminate_lease = leaseTormination

            # create attachment form

            unitAllocation = BlueMoonLeaseResponse.UtilityAllocations()
            unitAllocation.gas = responseData['standard']['addendum_utility_allocation_gas']
            unitAllocation.electricity = responseData['standard']['addendum_utility_allocation_electricity']
            unitAllocation.water = responseData['standard']['addendum_utility_allocation_water']
            unitAllocation.cable_tv = responseData['standard']['addendum_utility_allocation_cable_tv']
            unitAllocation.stormwater_drainage = responseData['standard']\
            ['addendum_utility_allocation_stormwater_drainage']
            unitAllocation.central_system_costs = responseData['standard']\
            ['addendum_utility_allocation_central_system_costs']
            unitAllocation.utility_trash = responseData['standard']['addendum_utility_allocation_trash']
            unitAllocation.govt_fees = responseData['standard']['addendum_utility_allocation_services_govt_fees']

            addendumUnitSubmetering = BlueMoonLeaseResponse.UnitSubmetering()
            addendumUnitSubmetering.gas = responseData['standard']['addendum_utility_submetering_gas']
            addendumUnitSubmetering.electricity = responseData['standard']['addendum_utility_submetering_electricity']
            addendumUnitSubmetering.water = responseData['standard']['addendum_utility_submetering_water']

            attachmentCopies = BlueMoonLeaseResponse.AttachmentCopies()
            attachmentCopies.access_gates = responseData['standard']['addendum_access_gate']
            attachmentCopies.special_provisions = responseData['standard']['addendum_additional_special_provisions']
            attachmentCopies.utility_allocation = unitAllocation
            attachmentCopies.animal_addendum = responseData['standard']['addendum_animal_addendum']
            attachmentCopies.apartment_rules = responseData['standard']['addendum_apartment_rules']
            attachmentCopies.asbestos = responseData['standard']['addendum_asbestos']
            attachmentCopies.bed_bug = responseData['standard']['addendum_bed_bug']
            attachmentCopies.early_termination = responseData['standard']['addendum_early_termination']
            attachmentCopies.enclosed_garage = responseData['standard']['addendum_enclosed_garage']
            attachmentCopies.intrusion_alarm = responseData['standard']['addendum_intrusion_alarm']
            attachmentCopies.inventory_and_condition = responseData['standard']['addendum_inventory_and_condition']
            attachmentCopies.hazard_disclosure = responseData['standard']['addendum_lead_hazard_disclosure']
            attachmentCopies.contract_guaranty = responseData['standard']['addendum_lease_contract_guaranty']
            attachmentCopies.housing = responseData['standard']['addendum_affordable_housing']
            attachmentCopies.description = responseData['standard']['addendum_legal_description']
            attachmentCopies.military_addendum = responseData['standard']['addendum_military_scra']
            attachmentCopies.mold = responseData['standard']['addendum_mold']
            attachmentCopies.cleaning_instructions = responseData['standard']['addendum_move_out_cleaning_instructions']
            attachmentCopies.notice_of_move = responseData['standard']['addendum_notice_of_intent_to_move_out']
            attachmentCopies.parking_permit_quantity = responseData['standard']['addendum_parking_permit_quantity']
            attachmentCopies.parking_permit = responseData['standard']['addendum_parking_permit']
            attachmentCopies.rent_concession = responseData['standard']['addendum_rent_concession']
            attachmentCopies.renters_insurance = responseData['standard']['addendum_renters_insurance']
            attachmentCopies.repair_request = responseData['standard']['addendum_repair_request_form']
            attachmentCopies.dish = responseData['standard']['addendum_satellite_dish']
            attachmentCopies.guidelines = responseData['standard']['addendum_security_guidelines']
            attachmentCopies.guidelines = responseData['standard']['tenant_guide']
            attachmentCopies.utility_submetering = addendumUnitSubmetering

            addendum_other, addendum_description = [], []
            for i in range(1, 5):
                other_addendum = 'addendum_other' + '_' + str(i)
                addendum_other.append(responseData['standard'][other_addendum])
            for i in range(1, 5):
                other_addendum_description = 'addendum_other1' + '_' + str(i) + '_' + 'description'
                addendum_description.append(responseData['standard'][other_addendum_description])
            attachmentCopies.other = addendum_other
            attachmentCopies.other_description = addendum_description

            attachmentLocateService = BlueMoonLeaseResponse.LocateService()
            attachmentLocateService.address = responseData['standard']['locator_address']
            attachmentLocateService.name = responseData['standard']['locator_name']
            attachmentLocateService.zip_code = responseData['standard']['locator_city_state_zip']
            attachmentLocateService.phone = responseData['standard']['locator_phone']

            ownerRepresentative = BlueMoonLeaseResponse.OwnerRepresentative()
            ownerRepresentative.address = responseData['standard']['owners_representative_address']
            ownerRepresentative.fax = responseData['standard']['owners_representative_fax']
            ownerRepresentative.telephone = responseData['standard']['owners_representative_telephone']
            ownerRepresentative.after_hours_phone = responseData['standard']['owners_representative_after_hours_phone']

            attachmentForm = BlueMoonLeaseResponse.AttachmentForm()
            attachmentForm.owner_representative = ownerRepresentative
            attachmentForm.locator_service = attachmentLocateService
            attachmentForm.copies_and_attachments = attachmentCopies

            # create animal addendum form
            petRules = BlueMoonLeaseResponse.PetRules()
            petRules.pet_inside = responseData['standard']['pet_urinate_inside_areas']
            petRules.pet_outside = responseData['standard']['pet_urinate_outside_areas']

            emergency = BlueMoonLeaseResponse.Emergence()
            emergency.doctor_name = responseData['standard']['pet_dr_name']
            emergency.address = responseData['standard']['pet_dr_address']
            emergency.city = responseData['standard']['pet_dr_city']
            emergency.phone = responseData['standard']['pet_dr_telephone']

            animalProvision = BlueMoonLeaseResponse.SpecialProvision()
            animalProvision.special_provision = responseData['standard']['pet_special_provisions']

            animalInformation = BlueMoonLeaseResponse.PetInformation()
            name, _type, breed, color, weight, age = [], [], [], [], [], []
            city_licence, licence, rabies_shot, house_broken, owner = [], [], [], [], []
            name.append(responseData['standard']['pet_name'])
            _type.append(responseData['standard']['pet_type'])
            breed.append(responseData['standard']['pet_breed'])
            color.append(responseData['standard']['pet_color'])
            weight.append(responseData['standard']['pet_weight'])
            age.append(responseData['standard']['pet_age'])
            city_licence.append(responseData['standard']['pet_license_city'])
            licence.append(responseData['standard']['pet_license_number'])
            rabies_shot.append(responseData['standard']['pet_date_of_last_shots'])
            house_broken.append(responseData['standard']['pet_house_broken'])
            owner.append(responseData['standard']['pet_owners_name'])
            for i in range(2, 4):
                name.append(responseData['standard']['pet_' + str(i) + '_' + 'name'])
                _type.append(responseData['standard']['pet_' + str(i) + '_' + 'type'])
                breed.append(responseData['standard']['pet_' + str(i) + '_' + 'breed'])
                color.append(responseData['standard']['pet_' + str(i) + '_' + 'color'])
                weight.append(responseData['standard']['pet_' + str(i) + '_' + 'weight'])
                age.append(responseData['standard']['pet_' + str(i) + '_' + 'age'])
                city_licence.append(responseData['standard']['pet_' + str(i) + '_' + 'license_city'])
                licence.append(responseData['standard']['pet_' + str(i) + '_' + 'license_number'])
                rabies_shot.append(responseData['standard']['pet_' + str(i) + '_' + 'date_of_last_shots'])
                house_broken.append(responseData['standard']['pet_' + str(i) + '_' + 'house_broken'])
                owner.append(responseData['standard']['pet_' + str(i) + '_' + 'owners_name'])

            animalInformation.name = name
            animalInformation.type = _type
            animalInformation.breed = breed
            animalInformation.color = color
            animalInformation.weight = weight
            animalInformation.age = age
            animalInformation.city_license = city_licence
            animalInformation.license_no = licence
            animalInformation.last_rabies_shot = rabies_shot
            animalInformation.housebroken = house_broken
            animalInformation.pet_owner = owner

            petAdditionalCharge = BlueMoonLeaseResponse.AdditionalPetCharges()
            petAdditionalCharge.pet_fees = responseData['standard']['pet_one_time_fee']
            petAdditionalCharge.monthly_rent = responseData['standard']['pet_additional_rent']
            petAdditionalCharge.security_deposite = responseData['standard']['pet_security_deposit']

            animalAddendum = BlueMoonLeaseResponse.AnimalAddendum()
            animalAddendum.additional_charges = petAdditionalCharge
            animalAddendum.information = animalInformation
            animalAddendum.emergency = emergency
            animalAddendum.special_provisions = animalProvision
            animalAddendum.pet_rules = petRules

            # create early lease
            earlySpecialProvision = BlueMoonLeaseResponse.EarlySpecialProvision()
            earlySpecialProvision.special_provision = responseData['standard']['early_termination_special_provisions']

            earlyLeaseCreation = BlueMoonLeaseResponse.EarlyLeaseTearm()
            earlyLeaseCreation.terminate_lease_last_day = responseData['standard']\
            ['early_termination_days_written_notice']
            earlyLeaseCreation.lease_terminate = responseData['standard']['early_termination_last_day_of_month']
            earlyLeaseCreation.lease_terminate_fee = responseData['standard']['early_termination_fee']
            earlyLeaseCreation.lease_terminate_notice_day = responseData['standard']\
            ['early_termination_fee_due_days_before_termination']
            earlyLeaseCreation.right_of_termination = responseData['standard']['early_termination_limited_to_fact']
            earlyLeaseCreation.lease_special_provision = earlySpecialProvision

            # create allocation addenda lease
            addendaCentralSystem = BlueMoonLeaseResponse.CentralSystemAllocation()
            addendaCentralSystem.combo_formula = responseData['standard']['ctrl_sys_util_adden_combo_formula_util']
            addendaCentralSystem.allocate_basis = responseData['standard']['ctrl_sys_util_adden_alloc_basis']
            addendaCentralSystem.formula = responseData['standard']['ctrl_sys_util_adden_formula']
            addendaCentralSystem.heat_ac = responseData['standard']['ctrl_sys_util_adden_heat_ac']
            addendaCentralSystem.hot_water = responseData['standard']['ctrl_sys_util_adden_hot_water']
            addendaCentralSystem.avg_basis = responseData['standard']['ctrl_sys_util_adden_monthly_avg_basis']
            addendaCentralSystem.water_avg_basis = responseData['standard']['ctrl_sys_util_adden_monthly_avg_hot_water']
            addendaCentralSystem.avg_hvac = responseData['standard']['ctrl_sys_util_adden_monthly_avg_hvac']
            addendaCentralSystem.sub_metered_formula = responseData['standard']\
            ['ctrl_sys_util_adden_submetered_formula_util']

            addendaTrashRemoval = BlueMoonLeaseResponse.TrashRemovalAddendum()
            addendaTrashRemoval.bill_based_on = responseData['standard']['trash_addendum_bill_based_on']
            addendaTrashRemoval.late_fee = responseData['standard']['trash_addendum_bill_late_fee']
            addendaTrashRemoval.administrative_fee = responseData['standard']['trash_addendum_administrative_fee']

            addandaStormWater = BlueMoonLeaseResponse.StormWaterAddendum()
            addandaStormWater.bill_based_on = responseData['standard']['stormwater_addendum_bill_based_on']
            addandaStormWater.administrative_fee = responseData['standard']['stormwater_addendum_administrative_fee']

            addendaGovtFee = BlueMoonLeaseResponse.GovernmentFeeAddendum()
            addendaGovtFee.cable_satelite = responseData['standard']['services_govt_fees_addendum_cable_satellite']
            addendaGovtFee.stormwater_drainage = responseData['standard']\
            ['services_govt_fees_addendum_stormwater_drainage']
            addendaGovtFee.addendum_trash = responseData['standard']['services_govt_fees_addendum_trash']
            addendaGovtFee.street_repair = responseData['standard']['services_govt_fees_addendum_street_repair']
            addendaGovtFee.emergency_services = responseData['standard']\
            ['services_govt_fees_addendum_emergency_services']
            addendaGovtFee.conservation_district = responseData['standard']\
            ['services_govt_fees_addendum_conservation_district']
            addendaGovtFee.inspection = responseData['standard']['services_govt_fees_addendum_inspection']
            addendaGovtFee.registration_license = responseData['standard']\
            ['services_govt_fees_addendum_registration_license']
            addendaGovtFee.late_fee = responseData['standard']['services_govt_fees_addendum_late_fee']
            addendaGovtFee.bill_based_on = responseData['standard']['services_govt_fees_addendum_bill_based_on']
            addendaGovtFee.administrative_fee = responseData['standard']\
            ['services_govt_fees_addendum_administrative_fee']
            addenda_other, addenda_description = [], []
            for i in range(1, 7):
                other = 'services_govt_fees_addendum_other' + '_' + str(i)
                description = 'services_govt_fees_addendum_other' + '_' + str(i) + '_desc'
                addenda_other.append(responseData['standard'][other])
                addenda_description.append(responseData['standard'][description])
            addendaGovtFee.other = addenda_other
            addendaGovtFee.other_desc = addenda_description

            addendaNaturalGas = BlueMoonLeaseResponse.NaturalGasAddendum()
            addendaNaturalGas.gas_allocation_fee = responseData['standard']['gas_allocation_late_fee']
            addendaNaturalGas.gas_allocation_formula = responseData['standard']['gas_allocation_formula']
            addendaNaturalGas.gas_allocation_duration = responseData['standard']['gas_allocation_deduction_percent']
            addendaNaturalGas.gas_allocation_administrative_fee = responseData['standard']\
            ['gas_allocation_administrative_fee']

            allocationAddendaForm = BlueMoonLeaseResponse.AllocationAddenda()
            allocationAddendaForm.national_gas_addendum = addendaNaturalGas
            allocationAddendaForm.government_fee_addendum = addendaGovtFee
            allocationAddendaForm.storm_water_addendum = addandaStormWater
            allocationAddendaForm.trash_removal_addendum = addendaTrashRemoval
            allocationAddendaForm.central_system_allocations = addendaCentralSystem

            # create misc. addenda lease
            installDryer = BlueMoonLeaseResponse.InstallDryer()
            installDryer.dryer = responseData['standard']['dryer_install']
            installDryer.washer = responseData['standard']['washer_install']

            shortLease = BlueMoonLeaseResponse.ShorLease()
            shortLease.special_provisions = responseData['standard']['short_lease_special_provisions']

            hangGuns = BlueMoonLeaseResponse.CarryingHandguns()
            hangGuns.conceal_area = responseData['standard']['gun_no_conceal_area']
            hangGuns.office = responseData['standard']['gun_no_conceal_office']
            hangGuns.property = responseData['standard']['gun_no_conceal_property']
            hangGuns.rooms = responseData['standard']['gun_no_conceal_rooms']
            hangGuns.open_carry_area = responseData['standard']['gun_no_open_carry_area']
            hangGuns.open_carry_office = responseData['standard']['gun_no_open_carry_office']
            hangGuns.open_carry_property = responseData['standard']['gun_no_open_carry_property']
            hangGuns.open_carry_rooms = responseData['standard']['gun_no_open_carry_rooms']

            trashRemoval = BlueMoonLeaseResponse.TrashRecycle()
            trashRemoval.bill_late_fee = responseData['standard']['trash_addendum_bill_late_fee']
            trashRemoval.recycling_flat_fee = responseData['standard']['addendum_trash_removal_recycling_flat_fee']
            trashRemoval.administrative_fee_flat = responseData['standard']['trash_addendum_administrative_fee_flat']

            dishSetup = BlueMoonLeaseResponse.Dish()
            dishSetup.no_dishes = responseData['standard']['satellite_addendum_no_dishes']
            dishSetup.insurance = responseData['standard']['satellite_addendum_insurance']
            dishSetup.security_deposit = responseData['standard']['satellite_addendum_security_deposit']
            dishSetup.security_deposit_days = responseData['standard']['satellite_addendum_security_deposit_days']

            patioMaintance = BlueMoonLeaseResponse.PatioMaintenance()
            patioMaintance.mowing = responseData['standard']['party_responsible_for_lawn_mowing']
            patioMaintance.watering = responseData['standard']['party_responsible_for_lawn_watering']
            patioMaintance.trash = responseData['standard']['party_responsible_for_lawn_trash']
            patioMaintance.fertilize = responseData['standard']['party_obligated_to_fertilize']

            smokingProvition = BlueMoonLeaseResponse.NoSmoking()
            smokingProvition.permitted_balcony = responseData['standard']\
            ['no_smoking_addendum_smoking_permitted_balcony']
            smokingProvition.permitted_outside = responseData['standard']\
            ['no_smoking_addendum_smoking_permitted_outside']
            smokingProvition.smoking_areas = responseData['standard']['no_smoking_addendum_smoking_areas']
            smokingProvition.smoking_distance = responseData['standard']['no_smoking_addendum_smoking_distance']

            noticeFOrMoveout = BlueMoonLeaseResponse.MoveOUtNotice()
            noticeFOrMoveout.notice_for_move_out = responseData['standard']['addendum_move_out_days_notice']

            legalDescription = BlueMoonLeaseResponse.LegalDescription()
            legalDescription.description = responseData['standard']['legal_description_of_unit']

            enclosedGarage = BlueMoonLeaseResponse.EnclosedGarage()
            enclosedGarage.carport_provided = responseData['standard']['garage_addendum_carport_provided']
            enclosedGarage.garage_space_no = responseData['standard']['garage_addendum_garage_space_no']
            enclosedGarage.carport_space_no = responseData['standard']['garage_addendum_carport_space_no']
            enclosedGarage.storage_unit_no = responseData['standard']['garage_addendum_storage_unit_no']
            enclosedGarage.opener_fine = responseData['standard']['garage_addendum_opener_fine']
            enclosedGarage.garage_key = responseData['standard']['garage_addendum_garage_key']
            enclosedGarage.garage_opener = responseData['standard']['garage_addendum_garage_opener']
            enclosedGarage.carport_provided = responseData['standard']['garage_addendum_garage_or_carport_provided']
            enclosedGarage.garage_provided = responseData['standard']['garage_addendum_garage_provided']

            electronicPayment = BlueMoonLeaseResponse.ElectronicPayment()
            electronicPayment.resident = residentInformation.resident
            rent = []
            for i in range(1, 7):
                resident = 'electronic_payment_addendum_resident' + '_' + str(i) + '_' + 'rent'
                rent.append(responseData['standard'][resident])
            electronicPayment.resident_rent = rent
            electronicPayment.special_provision = responseData['standard']['electronic_special_provision']

            micAddenda = BlueMoonLeaseResponse.MicAddenda()
            micAddenda.electronic_payment = electronicPayment
            micAddenda.enclosed_garage = enclosedGarage
            micAddenda.legal_description = legalDescription
            micAddenda.move_out_notice = noticeFOrMoveout
            micAddenda.no_smoking = smokingProvition
            micAddenda.patio_yard_maintenance = patioMaintance
            micAddenda.dish = dishSetup
            micAddenda.trash_recycle = trashRemoval
            micAddenda.carrying_handguns = hangGuns
            micAddenda.short_term_lease = shortLease
            micAddenda.install_dryer = installDryer

            # create Remote card code lease
            lustCardControll = BlueMoonLeaseResponse.RemoteLustCard()
            lustCardControll.lost_remote = responseData['standard']['remote_card_code_addendum_lost_remote']
            lustCardControll.replace_remote_fee = responseData['standard']\
            ['remote_card_code_addendum_replace_remote_fee']
            lustCardControll.lost_remote_deduct = responseData['standard']\
            ['remote_card_code_addendum_lost_remote_deduct']
            lustCardControll.addendum_lost_card = responseData['standard']['remote_card_code_addendum_lost_card']
            lustCardControll.replace_card_fee = responseData['standard']['remote_card_code_addendum_replace_card_fee']
            lustCardControll.lost_card_deduct = responseData['standard']['remote_card_code_addendum_lost_card_deduct']
            lustCardControll.addendum_code_change = responseData['standard']['remote_card_code_addendum_code_change']

            remoteCard = BlueMoonLeaseResponse.RemoteCardAccess()
            remoteCard.gate_access = responseData['standard']['remote_card_code_addendum_remote']
            remoteCard.add_card_fee = responseData['standard']['remote_card_code_addendum_add_card_fee']
            remoteCard.card = responseData['standard']['remote_card_code_addendum_card']
            remoteCard.add_remote_fee = responseData['standard']['remote_card_code_addendum_add_remote_fee']
            remoteCard.code = responseData['standard']['remote_card_code_addendum_code']

            remoteCardCode = BlueMoonLeaseResponse.RemoteCard()
            remoteCardCode.remote_control_code = lustCardControll
            remoteCardCode.remote_control_lust_damaged = remoteCard

            # create water and waste water
            electricAllocation = BlueMoonLeaseResponse.ElectricAllocationBill()
            electricAllocation.reconnect_fee = responseData['standard']['electric_service_reconnect_fee']
            electricAllocation.metering = responseData['standard']['addendum_utility_submetering']
            electricAllocation.square_feet_percent = responseData['standard']\
            ['electric_service_allocation_unit_square_feet_percent']
            electricAllocation.estimated_percent_use = responseData['standard']['electric_service_estimated_percent_use']
            electricAllocation.electric_method = responseData['standard']['electric_service_allocation_method']

            wasteWater = BlueMoonLeaseResponse.WaterWasteWater()
            wasteWater.average_monthly_bill = responseData['standard']['submeter_average_monthly_bill']
            wasteWater.lowest_monthly_bill = responseData['standard']['submeter_lowest_monthly_bill']
            wasteWater.highest_monthly_bill = responseData['standard']['submeter_highest_monthly_bill']
            wasteWater.service_fee = responseData['standard']['submeter_water_service_fee']
            wasteWater.from_date = responseData['standard']['submeter_water_consumption_from_date']
            wasteWater.to_date = responseData['standard']['submeter_water_consumption_to_date']
            wasteWater.bill_date = responseData['standard']['water_allocation_bill_date']
            wasteWater.method = responseData['standard']['tceq_water_allocation_method']

            electricityAndWater = BlueMoonLeaseResponse.ElectricWaterWasteWater()
            electricityAndWater.electric_allocation_bill = electricAllocation
            electricityAndWater.water_wasteWater = wasteWater

            # create Rent Concessions
            rentConcession = BlueMoonLeaseResponse.RentConcessions()
            rentConcession.concession_one_time = responseData['standard']['addendum_rent_concession_one_time']
            rentConcession.one_time_amount = responseData['standard']['addendum_rent_concession_one_time_amount']
            rentConcession.one_time_months = responseData['standard']['addendum_rent_concession_one_time_months']
            rentConcession.special_provisions = responseData['standard']['addendum_rent_concession_special_provisions']
            rentConcession.monthly_discount = responseData['standard']['addendum_rent_concession_monthly_discount']
            rentConcession.discounted_months = responseData['standard']['addendum_rent_concession_discounted_months']
            rentConcession.concession_amount = responseData['standard']['addendum_rent_concession_amount']

            # create Intrusion Alarm
            alarm = BlueMoonLeaseResponse.IntrusionAlarm()
            alarm.alarm = responseData['standard']['alarm_required']
            alarm.required_to_activate = responseData['standard']['alarm_permit_required_to_activate']
            alarm.activation_contact = responseData['standard']['alarm_permit_activation_contact']
            alarm.instructions_attached = responseData['standard']['alarm_instructions_attached']
            alarm.required_company = responseData['standard']['alarm_required_company']
            alarm.resident_chooses_company = responseData['standard']['alarm_resident_chooses_company']
            alarm.repair_contact = responseData['standard']['alarm_repair_contact']
            alarm.paid_by = responseData['standard']['alarm_repairs_paid_by']
            alarm.required_to_activate = responseData['standard']['alarm_company_required_to_activate']
            alarm.maintainer = responseData['standard']['alarm_maintainer']

            # create Additional Provisions
            activitesAddendum = BlueMoonLeaseResponse.ActivitiesAddendum()
            activitesAddendum.construction_provisions = responseData['standard']['construction_special_provisions']

            perPersonDwelling = BlueMoonLeaseResponse.RentalDwelling()
            perPersonDwelling.bedroom_sharing = responseData['standard']['per_person_bedroom_sharing']
            perPersonDwelling.sharing_common_areas = responseData['standard']['per_person_max_sharing_common_areas']
            perPersonDwelling.transfer_fee = responseData['standard']['per_person_transfer_fee']

            additionalProvision = BlueMoonLeaseResponse.AdditionalSpecialProvisions()
            additionalProvision.special_provision = responseData['standard']['additional_special_provisions']

            additionalSpecialProvision = BlueMoonLeaseResponse.AdditionalProvisions()
            additionalSpecialProvision.provisions = additionalProvision
            additionalSpecialProvision.rental_dwelling = perPersonDwelling
            additionalSpecialProvision.activities = activitesAddendum

            # create Renter Insurance
            rentInsurance = BlueMoonLeaseResponse.RenterInsurance()
            rentInsurance.liability_limit = responseData['standard']['renters_insurance_liability_limit']
            rentInsurance.insurance_default_fee = responseData['standard']['renters_insurance_default_fee']

            # create Lease Guaranty
            contractGuaranty = BlueMoonLeaseResponse.ContractGauranty()
            contractGuaranty.contract_guaranty = responseData['standard']['addendum_lease_contract_guaranty']

            leaseGauranty = BlueMoonLeaseResponse.LeaseGuaranty()
            leaseGauranty.date_for_renewal = responseData['standard']['guarantor_last_date_for_renewal']
            leaseGauranty.obligations = responseData['standard']['guarantor_length_of_obligations']
            leaseGauranty.contract = contractGuaranty

            # create summary_information
            summeryInformation = BlueMoonLeaseResponse.SummaryInformation()
            summeryInformation.address = responseData['standard']['address']
            summeryInformation.unit_number = responseData['standard']['unit_number']
            summeryInformation.start_date = responseData['standard']['lease_begin_date']
            summeryInformation.end_date = responseData['standard']['lease_end_date']
            summeryInformation.lease_termination = responseData['standard']\
            ['days_required_for_notice_of_lease_termination']
            summeryInformation.prorated = responseData['standard']['days_prorated']
            summeryInformation.security_deposit = responseData['standard']['security_deposit']
            summeryInformation.animal_deposit = responseData['standard']['security_deposit_includes_animal_deposit']
            summeryInformation.refund_check_payable = responseData['standard']['security_deposit_refund_check_payable']
            summeryInformation.check_mailed_to = responseData['standard']['security_deposit_refund_one_check_mailed_to']
            summeryInformation.apartment_keys = responseData['standard']['number_of_apartment_keys']
            summeryInformation.mail_keys = responseData['standard']['number_of_mail_keys']
            summeryInformation.other_keys = responseData['standard']['number_of_other_keys']
            summeryInformation.rent_concession = responseData['standard']['addendum_rent_concession']
            summeryInformation.pay_rent = responseData['standard']['pay_rent_address']
            summeryInformation.online_site = responseData['standard']['pay_rent_at_online_site']
            summeryInformation.on_site = responseData['standard']['pay_rent_on_site']
            summeryInformation.garage_in_rent = responseData['standard']['garage_cost_included_in_rent']
            summeryInformation.carport_in_rent = responseData['standard']['carport_cost_included_in_rent']
            summeryInformation.other_cost_in_rent = responseData['standard']['other_cost_included_in_rent']
            summeryInformation.storage_in_rent = responseData['standard']['storage_cost_included_in_rent']
            summeryInformation.washer_dryer_in_rent = responseData['standard']['washer_dryer_cost_included_in_rent']
            summeryInformation.gas = responseData['standard']['utilities_gas']
            summeryInformation.water = responseData['standard']['utilities_water']
            summeryInformation.trash = responseData['standard']['utilities_trash']
            summeryInformation.electricity = responseData['standard']['utilities_electricity']
            summeryInformation.cable_tv = responseData['standard']['utilities_cable_tv']
            summeryInformation.master_antenna = responseData['standard']['utilities_master_antenna']
            summeryInformation.internet = responseData['standard']['utilities_internet']
            summeryInformation.drainage = responseData['standard']['utilities_stormwater_drainage']
            summeryInformation.other = responseData['standard']['utilities_other']
            summeryInformation.insurance_requirement = responseData['standard']['renters_insurance_requirement']
            summeryInformation.due_date = responseData['standard']['rent_due_date']
            summeryInformation.prorated = responseData['standard']['prorated_rent']
            summeryInformation.rent_amount = responseData['standard']['rent']
            summeryInformation.initial_charge = responseData['standard']['late_charge_initial_charge']
            summeryInformation.percentage_of_rent = responseData['standard']['late_charge_percentage_of_rent']
            summeryInformation.daily_charge = responseData['standard']['late_charge_daily_charge']
            summeryInformation.daily_percent_of_rent = responseData['standard']['late_charge_daily_percent_of_rent']
            summeryInformation.check_charge = responseData['standard']['returned_check_charge']
            summeryInformation.additional_rent = responseData['standard']['pet_additional_rent']
            summeryInformation.pet_initial_charge = responseData['standard']['pet_charge_initial_charge']
            summeryInformation.pet_daily_charge = responseData['standard']['pet_charge_daily_charge']
            summeryInformation.monthly_pest_rent = responseData['standard']['monthly_pest_control_rent']
            summeryInformation.monthly_trash_rent = responseData['standard']['monthly_trash_rent']
            summeryInformation.electric_transfer_fee = responseData['standard']['electric_transfer_fee']
            summeryInformation.provisions = responseData['standard']['special_provisions']

            keyOfSummaryKeyInformation = BlueMoonLeaseResponse.SummaryKeyInformation()
            keyOfSummaryKeyInformation.summary_information = summeryInformation

            # creat covid19 form
            virusWaiver = BlueMoonLeaseResponse.VirusWarningWaiver()
            virusWaiver.waiver_signed_date = responseData['standard']['virus_waiver_signed_date']
            virusWaiver.waiver_signed_year = responseData['standard']['virus_waiver_signed_year']

            leasePaymentAgreements = BlueMoonLeaseResponse.PaymentAgreement()
            leasePaymentAgreements.date = responseData['standard']['pay_plan_lease_signed_date']
            leasePaymentAgreements.year = responseData['standard']['pay_plan_lease_signed_year']
            leasePaymentAgreements.current_month = responseData['standard']['pay_plan_due_current_month']
            leasePaymentAgreements.next_month = responseData['standard']['pay_plan_due_next_month']
            leasePaymentAgreements.due_time_period = responseData['standard']['pay_plan_due_time_period']
            leasePaymentAgreements.due_description = responseData['standard']['pay_plan_due_time_period_description']
            date, price = [], []
            for i in range(1, 13):
                pay_date = 'pay_plan_due_date' + '_' + str(i)
                pay_amount = 'pay_plan_amount' + '_' + str(i)
                date.append(responseData['standard'][pay_date])
                price.append(responseData['standard'][pay_amount])
            leasePaymentAgreements.due_date = date
            leasePaymentAgreements.amount = price

            leaseWaiverNotice = BlueMoonLeaseResponse.WaiverNotice()
            leaseWaiverNotice.begin_date = responseData['standard']['waiver_period_start_date']
            leaseWaiverNotice.end_date = responseData['standard']['waiver_period_end_date']
            leaseWaiverNotice.rent_due_date = responseData['standard']['waiver_period_rent_due_date']
            leaseWaiverNotice.phone_no = responseData['standard']['waiver_phone_contact']
            leaseWaiverNotice.email_id = responseData['standard']['waiver_email_contact']

            covidDetails = BlueMoonLeaseResponse.Covid19()
            covidDetails.notice_for_temporary_waiver = leaseWaiverNotice
            covidDetails.payment_plan_agreement = leasePaymentAgreements
            covidDetails.virus_warning_and_waiver = virusWaiver

            leadeHazardDetails = BlueMoonLeaseResponse.LeadHazard()
            leadeHazardDetails.paint_knowledge = responseData['standard']['lead_based_paint_knowledge']
            leadeHazardDetails.knowledge_comments = responseData['standard']['lead_based_paint_knowledge_comments']
            leadeHazardDetails.paint_reports = responseData['standard']['lead_based_paint_reports']
            leadeHazardDetails.reports_comment = responseData['standard']['lead_based_paint_reports_comments']

            leaseResponse.leaseTerms = sectionLeaseTerms
            leaseResponse.student_lease = studentLease
            leaseResponse.other_lease = otherCharges
            leaseResponse.special_provisions = leaseSpecialProvisions
            leaseResponse.attachment = attachmentForm
            leaseResponse.animal_addendum = animalAddendum
            leaseResponse.lead_hazard = leadeHazardDetails
            leaseResponse.early_terms = earlyLeaseCreation
            leaseResponse.allocation_addenda = allocationAddendaForm
            leaseResponse.mic_addenda = micAddenda
            leaseResponse.remote_card = remoteCardCode
            leaseResponse.electricity_water_waste_water = electricityAndWater
            leaseResponse.concessions = rentConcession
            leaseResponse.intrusion_alarm = alarm
            leaseResponse.additional_provision = additionalSpecialProvision
            leaseResponse.rent_insurance = rentInsurance
            leaseResponse.lease_guaranty = leaseGauranty
            leaseResponse.summary_key_information = keyOfSummaryKeyInformation
            leaseResponse.covid_details = covidDetails
            response.data = leaseResponse
            return True, response
        elif responseCode == 200:
            response.error.errorType = ErrorType.VALIDATION_ERROR.value
            response.error.errorMessages = responseData['errors']
            return False, response
        elif responseCode == 401:
            response.error.errorType = ErrorType.AUTHORIZATION_ERROR.value
            response.error.errorMessages = responseData['message']
            return False, response
        elif responseCode == 403:
            response.error.errorType = ErrorType.AUTHORIZATION_ERROR.value
            response.error.errorMessages = responseData['message']
            return False, response
        else:
            response.error.errorType = ErrorType.SYSTEM_ERROR.value
            return False, response

    def formatUpdateLeaseResponseData(self, _responseData: dict):
        response = BaseResponse()
        response.error = BaseError()
        responseCode = _responseData['responseCode']
        responseData = _responseData['responseMessage']
        if responseCode == 200:
            if responseData['success']:

                # the successful response of update lease API is exactly the same as create
                # lease successful response, hence utilizing the method formatCreateLeaseResponseData
                _data = {'responseCode': 201, 'responseMessage': responseData}
                isValid, response = self.formatCreateLeaseResponseData(_data)
                return isValid, response
            else:
                response.error.errorMessages = responseData['errors']
                return False, response
        elif responseCode == 401:
            response.error.errorType = ErrorType.AUTHORIZATION_ERROR.value
            response.error.errorMessages = responseData['message']
            return False, response
        elif responseCode == 403:
            response.error.errorType = ErrorType.AUTHORIZATION_ERROR.value
            response.error.errorMessages = responseData['message']
            return False, response
        elif responseCode == 404:
            response.error.errorMessages = 'Lease Not Found'
            return False, response
        else:
            response.error.errorType = ErrorType.SYSTEM_ERROR.value
            return False, response

    def formatDeleteLeaseResponseData(self, _responseData: dict):
        response = BaseResponse()
        response.error = BaseError()
        responseCode = _responseData['responseCode']
        responseData = _responseData['responseMessage']
        if responseCode == 200:
            response.data = responseData

            return True, response
        elif responseCode == 401:
            response.error.errorType = ErrorType.AUTHORIZATION_ERROR.value
            response.error.errorMessages = responseData['message']
            return False, response
        elif responseCode == 403:
            response.error.errorType = ErrorType.AUTHORIZATION_ERROR.value
            response.error.errorMessages = responseData['message']
            return False, response
        elif responseCode == 404:
            response.error.errorMessages = 'Lease Not Found'
            return False, response
        else:
            response.error.errorType = ErrorType.SYSTEM_ERROR.value
            return False, response

    def formatGetLeaseResponseData(self, _responseData: dict):
        response = BaseResponse()
        response.error = BaseError()
        responseCode = _responseData['responseCode']
        responseData = _responseData['responseMessage']
        if responseCode == 200:
            response.data = responseData

            return True, response
        elif responseCode == 401:
            response.error.errorType = ErrorType.AUTHORIZATION_ERROR.value
            response.error.errorMessages = responseData['message']
            return False, response
        elif responseCode == 403:
            response.error.errorType = ErrorType.AUTHORIZATION_ERROR.value
            response.error.errorMessages = responseData['message']
            return False, response
        elif responseCode == 404:
            response.error.errorMessages = 'Lease Not Found'
            return False, response
        else:
            response.error.errorType = ErrorType.SYSTEM_ERROR.value
            return False, response