import json
import logging

from bunch import bunchify

from DataPushPullShared.Utilities.DataController import DataValidation, Schema
from ExceptionHandling.Model.Exceptions import GatewayError, ValidationError, DataError, SecurityGatewayError
from ExceptionHandling.Utilities.ErrorCode import ErrorCode
from FunnelShared.Controller.FunnelGatewayController import FunnelGatewayController
from ResmanShared.Controller.ResmanGatewayController import ResmanGatewayController
from EntrataShared.Controller.EntrataGatewayController import EntrataGatewayController
from RealpageShared.Controller.RealpageGatewayController import RealpageGatewayController
from VendorShared.Model.ServiceRequest import Auth, ServiceRequest
from VendorShared.Utilities.VendorConstants import VendorConstants, PartnerConstants
from NewcoShared.Controller.NewcoGatewayController import NewcoGatewayController
from DataPushPullShared.Utilities.CacheController import CacheManager
from DataPushPullShared.Utilities.Entities import CommunityPartnerKeyValues, PartnerSecurity, Communities, CommunityPurposePartners, Partners
from VendorShared.Model.IPSResponse import CommunitySet

class IPSGateway:
    """
    IPSGateway is responsible for communicating with IPS internal service to get the platform information
    which will be helpful in communicating other partners.
    """
    _cache_obj = CacheManager()

    def get_platform_info(self, service_request: ServiceRequest):
        """
        Get platform information from IPS Service using communityUUID, customerUUID and purpose.
        Purpose = [Property, Residents, Units, Floor Plans, Prospects, Transaction, Charge code, Customer Events]

        Parameters
        ----------
        service_request : ServiceRequest
            The ServiceRequest Object
        """

        # Getting from cache if exists
        key = "{}:{}:{}:{}".format(service_request.payload[VendorConstants.COMMUNITY_UUID],
                                              service_request.payload[VendorConstants.CUSTOMER_UUID],
                                              service_request.purpose, VendorConstants.PLATFORM_DATA)
        output = self._cache_obj.get_from_cache(service_request, VendorConstants.VENDOR_INFO_CACHE,
                                                key, True)

        if output:
            logging.debug("Platform Response from cache success")
            return bunchify(output)

        # get platform object
        outgoing_platform_request = service_request.outgoing.plain_http[VendorConstants.GET_PLATFORM_OUTGOING_CHANNEL]
        response = outgoing_platform_request.conn.get(service_request.cid, self.__build_request_data(service_request))
        # Validate platform response
        self.__validate_ips_response(response.status_code)
        # Processing Response
        output = json.loads(response.text)
        logging.debug("Platform Response : {}".format(output))
        # Updating cache
        self._cache_obj.update_cache(service_request, VendorConstants.VENDOR_INFO_CACHE,
                                     key, output, 600.0, True)
        return bunchify(output)

    def get_partner_info(self, service_request: ServiceRequest, ips_response):
        """
        Get partner information from IPS Service returns the partners based on the CommunityID

        Parameters
        ----------
        service_request : ServiceRequest
            The ServiceRequest Object
        ips_response : response from the get_platform_info function
        """

        # Getting from cache if exists
        key = "{}:{}:{}:{}".format(service_request.payload[VendorConstants.COMMUNITY_UUID],
                                              service_request.payload[VendorConstants.CUSTOMER_UUID],
                                              service_request.purpose, VendorConstants.PARTNER_ID)
        output = self._cache_obj.get_from_cache(service_request, VendorConstants.VENDOR_INFO_CACHE,
                                                key, True)

        if output:
            logging.info("Partner Response from cache Success")
            return output

        # get partner info
        outgoing_platform_request = service_request.outgoing.plain_http[VendorConstants.GET_PARTNER_OUTGOING_CHANNEL]
        response = outgoing_platform_request.conn.get(service_request.cid,
                                                      self.__build_request_data_partner(service_request))
        # Validate Partner response
        self.__validate_ips_response(response.status_code)
        # Processing Response
        partner_response = json.loads(response.text)
        logging.info("Partner Response from IPS: Success")
        # Sample Partner Response From IPS
        # "content": [
        #    {
        #    "uuid": "---PARTNER UUID HERE----",
        #    "name": "---PARTNER NAME HERE----",
        #    "logoUrl": null,
        #    }
        #  ]
        for i in partner_response[VendorConstants.CONTENT]:
            if i[VendorConstants.NAME] == ips_response.platformData.platform:
                # Updating cache
                self._cache_obj.update_cache(service_request, VendorConstants.VENDOR_INFO_CACHE,
                                             key, i[VendorConstants.UUID], 600.0, True)
                return i[VendorConstants.UUID]
        return None

    def get_security_info(self, service_request: ServiceRequest, uuid: str):

        # Getting from cache if exists
        key = "{}:{}:{}:{}".format(service_request.payload[VendorConstants.COMMUNITY_UUID],
                                              service_request.payload[VendorConstants.CUSTOMER_UUID],
                                              service_request.purpose, VendorConstants.CREDENTIALS)
        output = self._cache_obj.get_from_cache(service_request, VendorConstants.VENDOR_INFO_CACHE,
                                                key, True)
        if output:
            logging.info("Security Response from cache: Success")
            return output

        # get security info
        outgoing_platform_request = service_request.outgoing.plain_http[VendorConstants.GET_SECURITY_OUTGOING_CHANNEL]
        response = outgoing_platform_request.conn.get(service_request.cid, self.__build_request_data_security(uuid))
        # Validate Security response
        self.__validate_ips_response(response.status_code)
        # Processing Response
        security_response = json.loads(response.text)
        logging.info("Security Response from IPS: Success")
        # Sample Security Response From IPS
        # {
        # "content": [
        #     {
        #         "partner_uuid": "d6cb517b-df8a-47e3-af49-d43953465877",
        #         "partner_name": "ResMan",
        #         "security": {
        #             "credentials": [
        #                 {
        #                     "body": {
        #                        "key" : "value"
        #                     },
        #                     "headers": [],
        #                     "partner": "ResMan"
        #                 }
        #             ]
        #         }
        #     }
        #    ]
        # }

        if VendorConstants.CREDENTIALS in security_response[VendorConstants.CONTENT][0][
            VendorConstants.SECURITY].keys():
            if VendorConstants.BODY in security_response[VendorConstants.CONTENT][0][VendorConstants.SECURITY][
                VendorConstants.CREDENTIALS][0].keys():
                output = \
                    security_response[VendorConstants.CONTENT][0][VendorConstants.SECURITY][
                        VendorConstants.CREDENTIALS][0][VendorConstants.BODY]

                # Updating cache
                self._cache_obj.update_cache(service_request, VendorConstants.VENDOR_INFO_CACHE,
                                             key, output, 600.0, True)
                return output
            else:
                logging.debug("Security Config from IPS : Failed")
                return None
        else:
            logging.debug("Security Config from IPS : Failed")
            return None

    def __build_request_data_partner(self, service_request: ServiceRequest):
        """
        Build the request data which is used to call IPS service to get Partner data.

        Parameters
        ----------
        service_request : ServiceRequest
            The ServiceRequest Object

        Returns
        -------
        data : Dict (Partner)
            request_data used to call IPS Partner Endpoint
        """

        # Creating Partner request data
        data = {
            VendorConstants.COMMUNITY_UUID: service_request.payload[VendorConstants.COMMUNITY_UUID]
        }
        return data

    def __build_request_data_security(self, uuid: str):
        """
        Build the request data which is used to call IPS service to get Security data.

        Parameters
        ----------
        uuid : str
            The PARTNER_ID

        Returns
        -------
        data : Dict (Security)
            request_data used to call IPS Security Endpoint
        """

        # Creating Security request data
        data = {
            VendorConstants.PARTNER_ID: uuid
        }
        return data

    def __build_request_data(self, service_request: ServiceRequest):
        """
        Build the request data which is used to call IPS service to get platform data.

        Parameters
        ----------
        service_request : ServiceRequest
            The ServiceRequest Object

        Returns
        -------
        platform_request_data : Dict
            request_data used to call IPS Service
        """

        # Creating Platform request data
        platform_request_data = {
            VendorConstants.COMMUNITY_UUID: service_request.payload[VendorConstants.COMMUNITY_UUID],
            VendorConstants.CUSTOMER_UUID: service_request.payload[VendorConstants.CUSTOMER_UUID],
            VendorConstants.PURPOSE: service_request.purpose
        }
        return platform_request_data

    def __validate_ips_response(self, _response_code):
        if _response_code != 200:
            raise GatewayError(ErrorCode.ERROR_HTTP_0001, VendorConstants.INVALID_DATA, VendorConstants.BAD_REQUEST)
    
    def get_source_info(self, service_request: ServiceRequest):
        """
        This function return the source partner name using API key sent in service request
        """
        outgoing_platform_request = service_request.outgoing.plain_http[VendorConstants.GET_SECURITY_OUTGOING_CHANNEL]
        response = outgoing_platform_request.conn.get(service_request.cid, self.__build_request_data_security(uuid = ""))
        # Validate Security response
        self.__validate_ips_response(response.status_code)
        # Processing Response
        security_response = json.loads(response.text)
        for item in security_response[VendorConstants.CONTENT]:
            if item[VendorConstants.SECURITY].get(VendorConstants.APIKEY):
                if item[VendorConstants.SECURITY][VendorConstants.APIKEY] == service_request.payload[VendorConstants.APIKEY]:
                    return {VendorConstants.SOURCE: VendorConstants.SOURCE_SYSTEM.get(item[VendorConstants.PARTNER_NAME]) and VendorConstants.SOURCE_SYSTEM[item[VendorConstants.PARTNER_NAME]] or None}


class VendorRouter:
    """
    VendorRouter for finding the respective vendor based on the IPS response
    """
    __ips_gateway = IPSGateway()
    """
    List of vendors to skip security validation
    """
    skip_security_info_vendors = [PartnerConstants.NEWCO]

    def resolve_vendor(self, service_request: ServiceRequest):
        """
        Call the IPS service and resolve the vendor based the IPS response

        Parameters
        ----------
        service_request : ServiceRequest
            The input request
        """
        # Validating the request payload before calling IPSGateway
        self.__validate(service_request)
        # Calling IPSGateway.get_platform_info to get platform info
        ips_response = self.__ips_gateway.get_platform_info(service_request)
        return self.__get_vendor_object(ips_response, service_request)

    def __validate(self, service_request: ServiceRequest):
        """
        Validate the request object before IPS call
        Parameters
        ----------
        service_request : ServiceRequest
            The input request
        """
        _isValid, _errors = DataValidation.schema(Schema.PLATFORM_DATA, service_request.payload)
        if _errors:
            raise ValidationError(ErrorCode.ERROR_DATA_0001, _errors)

    def __get_vendor_object(self, ips_response, service_request: ServiceRequest):
        """
        Get Vendor Gateway Object for the given input
        """

        switcher = {
            PartnerConstants.RESMAN: ResmanGatewayController,
            PartnerConstants.ENTRATA: EntrataGatewayController,
            PartnerConstants.NEWCO: NewcoGatewayController,
            PartnerConstants.REALPAGE: RealpageGatewayController,
            PartnerConstants.FUNNEL: FunnelGatewayController
        }
        #ignore_config = [PartnerConstants.FUNNEL]
        api_config, source_info = {} , {}
        if (not ips_response) or (not ips_response.platformData):
            raise DataError(ErrorCode.ERROR_DATA_0001, VendorConstants.INVALID_DATA)

        # Capturing ips_response in service request platformdata
        service_request.platformdata = ips_response

        vendor_object = switcher.get(ips_response.platformData.platform, None)

        if not vendor_object:
            raise DataError(ErrorCode.ERROR_DATA_0001, VendorConstants.INVALID_DATA)

        if ips_response.platformData.platform not in self.skip_security_info_vendors:
            partner_id = self.__ips_gateway.get_partner_info(service_request, ips_response)
            if not partner_id:
                raise DataError(ErrorCode.ERROR_DATA_0001, VendorConstants.INVALID_DATA)

            api_config = self.__ips_gateway.get_security_info(service_request, partner_id)
            if not api_config:
                raise SecurityGatewayError(ErrorCode.ERROR_DATA_0001, VendorConstants.INVALID_SECURITY)

            source_info = self.__ips_gateway.get_source_info(service_request)
            logging.debug("source information %s" %source_info)
            if not source_info:
                raise SecurityGatewayError(ErrorCode.ERROR_DATA_0001, VendorConstants.INVALID_SOURCE)
            
            auth_config = api_config
            auth_config.update(ips_response.platformData)
            auth_config.update(source_info)
            logging.info("API Configuration Update: Success")
            service_request.auth = Auth(auth_config)
        return vendor_object()

    def get_communities_info(self, service_request: ServiceRequest):
        """
        This method returns list of all community objects or specific communities received in input payload. 
        """
        logging.info("Get communities list")
        session = service_request.outgoing.sql.get(VendorConstants.IPS_DB).session()
        logging.info("session creation is success")

        switcher = {
                PartnerConstants.RESMAN: ResmanGatewayController,
                PartnerConstants.ENTRATA: EntrataGatewayController,
                PartnerConstants.NEWCO: NewcoGatewayController,
                PartnerConstants.REALPAGE: RealpageGatewayController,
                PartnerConstants.FUNNEL: FunnelGatewayController
            }
        
        community_id = service_request.payload[VendorConstants.COMMUNITY_UUID]

        
        if service_request.payload[VendorConstants.COMMUNITY_UUID]:
            logging.info("commmunities based on community_UUID provided")
            result = session.query(Communities
                            ).join(CommunityPurposePartners, Communities.community_uuid == CommunityPurposePartners.community_uuid
                            ).join(Partners, CommunityPurposePartners.partner_name == Partners.partner_name
                            ).join(PartnerSecurity, PartnerSecurity.partner_uuid == Partners.partner_uuid, isouter = True
                            ).join(CommunityPartnerKeyValues, CommunityPartnerKeyValues.partner_name == Partners.partner_name, isouter = True
                                ).filter(Communities.customer_uuid==service_request.payload[VendorConstants.CUSTOMER_UUID]
                                    , Communities.community_uuid.in_(community_id)
                                    ).with_entities(Communities.community_uuid, CommunityPartnerKeyValues.key_name,
                                            CommunityPartnerKeyValues.key_value,Partners.partner_uuid
                                            ,Partners.partner_name, PartnerSecurity.security
                                            ).order_by(Communities.community_uuid.desc()
                                                    ).all()

        else:
            logging.info("all commmunities")
            result = session.query(Communities
                            ).join(CommunityPurposePartners, Communities.community_uuid == CommunityPurposePartners.community_uuid
                            ).join(Partners, CommunityPurposePartners.partner_name == Partners.partner_name
                            ).join(PartnerSecurity, PartnerSecurity.partner_uuid == Partners.partner_uuid, isouter = True
                            ).join(CommunityPartnerKeyValues, CommunityPartnerKeyValues.partner_name == Partners.partner_name, isouter = True
                                ).filter(Communities.customer_uuid==service_request.payload[VendorConstants.CUSTOMER_UUID]
                                    ).with_entities(Communities.community_uuid, CommunityPartnerKeyValues.key_name,
                                            CommunityPartnerKeyValues.key_value,Partners.partner_uuid, 
                                            Partners.partner_name, PartnerSecurity.security
                                            ).order_by(Communities.community_uuid.desc()
                                                    ).all()
        
        source_info = self.__ips_gateway.get_source_info(service_request)
        logging.debug("source information %s" %source_info)
        if not source_info:
            raise SecurityGatewayError(ErrorCode.ERROR_DATA_0001, VendorConstants.INVALID_SOURCE)
        logging.info(result)
        community_set = CommunitySet()
        resultlist = []
        
        for community in result:
            if community_set.community_id != community.community_uuid:
                platformdata = {}
                community_set = CommunitySet()
                community_set.community_id = community.community_uuid
                community_set.partner_id = community.partner_uuid
                if community.security.get(VendorConstants.CREDENTIALS):
                    if VendorConstants.BODY in community.security[VendorConstants.CREDENTIALS][0].keys():
                        output = \
                            community.security[VendorConstants.CREDENTIALS][0][VendorConstants.BODY]
                        output.update(source_info)
                    else:
                        logging.debug("Security Config from IPS : Failed")
                else:
                    logging.debug("Security Config from IPS : Failed")
                community_set.security = output
                community_set.partner_object = switcher.get(community.partner_name, None)
                if community_set.partner_object:
                    community_set.partner_object = community_set.partner_object()
                community_set.partner_name = community.partner_name
                resultlist.append(community_set)
            platformdata[community.key_name] = community.key_value
            community_set.platformdata = platformdata
        return resultlist
