import os
import datetime, json, logging, requests
from datetime import  datetime, timedelta
from constants.realpage_constants import RealpageConstants
from configuration.realpage.realpage_config import ilm_config
import suds

from env_reader import EnvReader

env_instance = EnvReader.get_instance().get_ips_envs()


class DataRealpage:
        
    def get_tour_availability(self, partners, event, ips_response):
        """
        Get tour availability from Realpage
        """
        
        logging.info("Availability: RealPage")  
        response_list = self.get_available_times(partners, event, ips_response)
        if len(response_list) > 0:
            return response_list

        elif len(response_list) == 0:
            logging.warn("RealPage services is not responding or has provided an empty payload.")
            return []
        
    def get_available_times(self, partners , payload, ips_response):
        """
        Returns the available times based on the start date and end date
        """
        outgoingIPSPartnerChannelResponse = partners
        partner = ips_response["purpose"]["guestCards"]["partner_name"]
        ips_partner_response = outgoingIPSPartnerChannelResponse
        partner_uuid = ips_partner_response[0]['partner']['partnerId'] if (ips_partner_response and
                                                                           len(ips_partner_response) > 0 and
                                                                           ips_partner_response[0]) else ""

        api_creds = ""
        outgoingIPSSecurityResponse = ""
        pmcid = ""
        siteid = ""
        licensekey = ""
        client = None
        if partner_uuid != "":  
                headers = {
                    'Content-Type': 'application/json',
                    'apikey': env_instance['api_key'],
                    'x-ips-consumer-id': env_instance['consumer_id']
                }
                outgoingIPSSecurityResponse = requests.get(
                    f'{env_instance["ips_host"]}/api/v2/partner/partner-security/security-v1/{partner_uuid}', headers=headers)
                security_response = outgoingIPSSecurityResponse.json()

                #CREATING CLIENT CONNECTION WITH API CREDENTIALS RETURNED FROM SECURITY RESPONSE
                if isinstance(security_response, dict) and security_response and security_response.get(RealpageConstants.PARTNER_NAME) == RealpageConstants.REALPAGE:
                    api_creds = security_response[RealpageConstants.SECURITY][RealpageConstants.CREDENTIALS][0][RealpageConstants.BODY][RealpageConstants.DH] # getting api credentials
                    imp = suds.xsd.doctor.Import(RealpageConstants.IMPORT_HOST, location=RealpageConstants.IMPORT_LOCATION)
                    imp.filter.add(RealpageConstants.XML_SOAP)
                    doctor = suds.xsd.doctor.ImportDoctor(imp)
                    client = suds.Client(api_creds[RealpageConstants.WSDL], doctor=doctor)  # creating client connection
                    pmcid = api_creds[RealpageConstants.PMCID]
                    siteid = api_creds[RealpageConstants.SITEID]
                    licensekey = api_creds[RealpageConstants.LICENSE_KEY]

        if not client:
            client = suds.Client(f"{ilm_config['ilm_host']}" if partner.lower() in ["realpage_ilm", "realpage_l2l"] else RealpageConstants.DHWSDL)  # creating client connection

        factory = client.factory
        # Preparing auth details from service request
        _auth = client.factory.create(RealpageConstants.AUTHDTO)
        _auth.pmcid = pmcid if pmcid != "" else ips_response["params"]["foreign_customer_id"]
        _auth.siteid = siteid if siteid != "" else ips_response["params"]["foreign_community_id"]
        _auth.licensekey = ilm_config[f"ws_realpage_ilm_apikey"] if partner in ["realpage_ilm", "realpage_l2l"] else licensekey
        date_diff = datetime.strptime(payload[RealpageConstants.TIME_DATA][RealpageConstants.TO_DATE], RealpageConstants.TIMEFORMAT) - \
                    datetime.strptime(payload[RealpageConstants.TIME_DATA][RealpageConstants.FROM_DATE], RealpageConstants.TIMEFORMAT)
        toDate = payload[RealpageConstants.TIME_DATA][RealpageConstants.TO_DATE]
        if date_diff.days > 7:
            toDate = (datetime.strptime(payload[RealpageConstants.TIME_DATA][RealpageConstants.FROM_DATE], RealpageConstants.TIMEFORMAT) +
                    timedelta(days=7)).strftime(RealpageConstants.TIMEFORMAT)

        getappointmenttimesparam = factory.create(RealpageConstants.GET_APPOINTMENT_PARAM)
        
        # Set the attributes of the getappointmenttimesparam object
        getappointmenttimesparam.checkall = False
        getappointmenttimesparam.leasingagentid = RealpageConstants.LEASING_AGENT_ID
        getappointmenttimesparam.startdatetime = self.format_timestamp(payload[RealpageConstants.TIME_DATA][RealpageConstants.FROM_DATE] + RealpageConstants.START_TIME)
        getappointmenttimesparam.enddatetime = self.format_timestamp(toDate + RealpageConstants.END_TIME)
        response = client.service.getagentsappointmenttimes(auth=_auth, getappointmenttimesparam=getappointmenttimesparam)
        
        response_list = []
     
        logging.info("Available Dates")
        for i in response[RealpageConstants.GET_APPOINTMENT_TIMES][RealpageConstants.LEASING_AGENT]:
            i = dict([i])
            if i.get(RealpageConstants.AVAILABLE_DATES):
                if RealpageConstants.AVAILABLE_DATE in i[RealpageConstants.AVAILABLE_DATES]:
                    available_dates = i[RealpageConstants.AVAILABLE_DATES][RealpageConstants.AVAILABLE_DATE]
                    if isinstance(available_dates, list):
                        response_list.extend(available_dates)
                    elif isinstance(available_dates, dict):
                        response_list.append(available_dates)
                    else:
                        response_list.append(available_dates)
        
        return self.generate_time_slots(response_list)

    def generate_time_slots(self, input_dict):
        '''
        Method to tour availability time slots based on input list of dict
        '''
        final_result = []
        for i in range(len(input_dict)):
           
            start, end = input_dict[i]
            res = []
            start_time = datetime.strptime(start[1], RealpageConstants.TIMEFORMAT)
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
            sth,stm = start_time.hour,start_time.minute
            end_time = datetime.strptime(end[1], '%Y-%m-%dT%H:%M:%S')
            end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
            eth,etm = end_time.hour, end_time.minute
            if (abs(sth-eth) in (0,1) and abs(stm-etm) in (15,45)) :
                continue;
            maximum = max(sth,eth)
            if sth == maximum:
                res.append(start_time_str)
                while sth >= eth:
                    if (sth==eth and (stm-etm)<=15) :
                        break;
                    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
                    final_time = start_time - timedelta(minutes = 30)
                    final_time_str = final_time.strftime('%Y-%m-%d %H:%M:%S')
                    res.append(final_time_str)
                    start_time = final_time
                    sth,stm = final_time.hour, final_time.minute
            elif eth == maximum:
                res.append(end_time_str)
                while eth >= sth:
                    if (sth==eth and (etm-stm)<=15) :
                        break;
                    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
                    final_time = end_time - timedelta(minutes = 30)
                    final_time_str = final_time.strftime('%Y-%m-%d %H:%M:%S')
                    res.append(final_time_str)
                    end_time = final_time
                    eth,etm = final_time.hour, final_time.minute
            final_result += res
        return sorted(list(set(final_result)))
    
    def format_timestamp(self, timestamp_str):
        # Extract the UTC time part
        utc_time_str = timestamp_str[:19] + "Z"
        timestamp_utc = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")

        # Extract the separate time part
        separate_time_str = timestamp_str[-8:]
        separate_time = datetime.strptime(separate_time_str, "%H:%M:%S").time()

        # Combine the UTC date and separate time
        combined_timestamp = datetime.combine(timestamp_utc.date(), separate_time)

        # Format the datetime object as a string with UTC offset
        formatted_timestamp = combined_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

        return formatted_timestamp
