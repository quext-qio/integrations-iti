import datetime, logging
from datetime import  datetime, timedelta
from Utils.Constants.RealpageConstants import RealpageConstants
from configuration.realpage_config import ilm_config
import suds


class DataRealpage:
        
    def get_tour_availability(self, ips_response, input):
        """
        Get tour availability from Realpage
        """
        
        logging.info("Availability: RealPage")  
        response_list = self.get_available_times(input, ips_response)
        if len(response_list) > 0:
            return response_list, {}

        elif len(response_list) == 0:
            logging.warn("RealPage services is not responding or has provided an empty payload.")
            
        return [], {"message": "Please contact the leasing office by phone to schedule a tour."}
        
    def get_available_times(self, payload, ips_response):
        """
        Returns the available times based on the start date and end date
        """
        partner = ips_response["purpose"]["tourAvailability"]["partner_name"]
     
        licensekey = ilm_config[f"dh_realpage_onsite_apikey"]
        client = None
       
        client = suds.Client(RealpageConstants.ILMWSDL if partner.lower() in ["realpage_ilm", "realpage_l2l"] else RealpageConstants.DHWSDL)  # creating client connection

        factory = client.factory
        # Preparing auth details from service request
        _auth = client.factory.create(RealpageConstants.AUTHDTO)
        _auth.pmcid = ips_response["params"]["foreign_customer_id"]
        _auth.siteid = ips_response["params"]["foreign_community_id"]
        _auth.licensekey = ilm_config[f"ws_realpage_ilm_apikey"] if partner.lower() in ["realpage_ilm", "realpage_l2l"] else licensekey
        
        date_diff = datetime.strptime(payload[RealpageConstants.TIME_DATA][RealpageConstants.TO_DATE], RealpageConstants.DAYFORMAT) - \
                    datetime.strptime(payload[RealpageConstants.TIME_DATA][RealpageConstants.FROM_DATE], RealpageConstants.DAYFORMAT)
        toDate = payload[RealpageConstants.TIME_DATA][RealpageConstants.TO_DATE]
        if date_diff.days > 7:
            toDate = (datetime.strptime(payload[RealpageConstants.TIME_DATA][RealpageConstants.FROM_DATE], RealpageConstants.DAYFORMAT) +
                    timedelta(days=7)).strftime(RealpageConstants.DAYFORMAT)

        getappointmenttimesparam = factory.create(RealpageConstants.GET_APPOINTMENT_PARAM)
        
        # Set the attributes of the getappointmenttimesparam object
        getappointmenttimesparam.checkall = False
        getappointmenttimesparam.leasingagentid =  "0" if partner.lower() in ["realpage_ilm", "realpage_l2l"] else RealpageConstants.LEASING_AGENT_ID
        getappointmenttimesparam.startdatetime = payload[RealpageConstants.TIME_DATA][RealpageConstants.FROM_DATE] + RealpageConstants.START_TIME
        getappointmenttimesparam.enddatetime = toDate + RealpageConstants.END_TIME
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
            start_time = datetime.strptime(start[1], '%Y-%m-%dT%H:%M:%S')
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


