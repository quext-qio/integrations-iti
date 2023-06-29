import os
import datetime, json, logging
import suds


class DataRealpage:
        
    def get_tour_availability(self, ips, event):
        """
        Get tour availability from Realpage
        """
            
        logging.info("Availability: RealPage")  
        response_list = self.get_available_times(input.platformData.communityUUID,self, input)
        if len(response_list) > 0:
            self.response.status_code = 200
            self.response.payload = {
                    "data": {
                    "availableTimes": response_list
                    },
                "error": {}
            } 

        elif len(response_list) == 0:
            self.logger.warning("RealPage services is not responding or has provided an empty payload.")
            self.response.status_code = 409
            self.response.payload = {
                "data": {},
                "error": {
                    "message": "Please contact the leasing office by phone to schedule a tour.",
                }
            }   
        return
        
    def get_available_times(self, community_id:str, service_obj, payload):
        """
        Returns the available times based on the start date and end date
        """
        _partnerpayload = {
            "communityUUID": community_id
        }
        partner_uuid_cache = service_obj.cache.get_cache('builtin', 'default')

        if 'partner_uuid' not in partner_uuid_cache:
            outgoingIPSPartnerChannel = service_obj.outgoing.plain_http[VendorConstants.GET_PARTNER_OUTGOING_CHANNEL]
            outgoingIPSPartnerChannelResponse = outgoingIPSPartnerChannel.conn.get(service_obj.cid, _partnerpayload)
            ips_partner_response = json.loads(outgoingIPSPartnerChannelResponse.text)
            partner_uuid = ips_partner_response['content'][0]['uuid'] if ips_partner_response.get('content') and len(
                ips_partner_response.get('content')) > 0 else ""
            partner_uuid_cache.set('partner_uuid', partner_uuid)
        else:
            partner_uuid = partner_uuid_cache.get('partner_uuid')

        api_creds = ""
        outgoingIPSSecurityResponse = ""
        pmcid = ""
        siteid = ""
        licensekey = ""
        client = None
        if partner_uuid:  # and input.get("source"):
            security_response_cache = service_obj.cache.get_cache('builtin', 'default')
            if 'security_response' not in security_response_cache:
                outgoingIPSSecurityChannel = service_obj.outgoing.plain_http[VendorConstants.GET_SECURITY_OUTGOING_CHANNEL]
                outgoingIPSSecurityResponse = outgoingIPSSecurityChannel.conn.get(service_obj.cid,
                                                                                dict(partnerUUID=partner_uuid))
                security_response = json.loads(outgoingIPSSecurityResponse.text)
                security_response_cache.set('security_response', security_response)
            else:
                security_response = security_response_cache.get('security_response')

            if len(security_response["content"]) > 0:
                for i in security_response["content"]:
                    if i["partner_name"] == PartnerConstants.REALPAGE:
                        api_creds = i["security"]["credentials"][0]["body"]["DH"]  # if input["source"]==VendorConstants.DH else i["security"]["credentials"][0]["body"]["WS"]
                        imp = Import('http://www.w3.org/2001/XMLSchema', location='http://www.w3.org/2001/XMLSchema.xsd')
                        imp.filter.add('http://xml.apache.org/xml-soap')
                        doctor = ImportDoctor(imp)
                        client = Client(api_creds["wsdl"], doctor=doctor)  # creating client connection
                        pmcid = api_creds["pmcid"]
                        siteid = api_creds["siteid"]
                        licensekey = api_creds["licensekey"]
                        break

        if not client:
            client = Client(VendorConstants.DHWSDL)  # creating client connection

        factory = client.factory
        # Preparing auth details from service request
        _auth = factory.create('AuthDTO', pmcid=pmcid, siteid=siteid, licensekey=licensekey)

        date_diff = datetime.strptime(payload.timeData.toDate, RealpageConstants.DAYFORMAT) - \
                    datetime.strptime(payload.timeData.fromDate, RealpageConstants.DAYFORMAT)
        toDate = payload.timeData.toDate
        if date_diff.days > 7:
            toDate = (datetime.strptime(payload.timeData.fromDate, RealpageConstants.DAYFORMAT) +
                    timedelta(days=7)).strftime(RealpageConstants.DAYFORMAT)

        getappointmenttimesparam = factory.create('getappointmenttimesparam',
                                                checkall='False',
                                                leasingagentid=RealpageConstants.LEASING_AGENT_ID,
                                                startdatetime=payload.timeData.fromDate + RealpageConstants.START_TIME,
                                                enddatetime=toDate + RealpageConstants.END_TIME)

        response = client.service.getagentsappointmenttimes(auth=_auth,
                                                            getappointmenttimesparam=getappointmenttimesparam)

        v = client.validator
        v.allow_unknown = True
        result = client.dict(response)
        isValid = v(result,
                    RealpageConstants.Validation_Schema[RealpageConstants.Schema.REAL_PAGE_GET_AGENT_APPOINTMENT_TIME])

        response_list = []
        logging.info("Available Dates")
        if isValid:
            leasing_agents = result["getagentsappointmenttimes"]['leasingagent']
            if isinstance(leasing_agents, list):
                for i in leasing_agents:
                    if i.get('availabledates') and isinstance(i['availabledates']['availabledate'], list):
                        response_list.extend(i['availabledates']['availabledate'])
                    elif i.get('availabledates') and isinstance(i['availabledates']['availabledate'], dict):
                        response_list.append(i['availabledates']['availabledate'])
            elif isinstance(leasing_agents, dict):
                if leasing_agents.get('availabledates') and isinstance(leasing_agents['availabledates']['availabledate'], list):
                    response_list.extend(leasing_agents['availabledates']['availabledate'])
                elif leasing_agents.get('availabledates') and isinstance(leasing_agents['availabledates']['availabledate'], dict):
                    response_list.append(leasing_agents['availabledates']['availabledate'])

        return generate_time_slots(response_list)

    def generate_time_slots(self, input_dict):
        '''
        Method to tour availability time slots based on input list of dict
        '''
        final_result = []
        for i in range(len(input_dict)):
            start, end = input_dict[i].values()
            res = []
            start_time = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
            sth,stm = start_time.hour,start_time.minute
            end_time = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')
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


