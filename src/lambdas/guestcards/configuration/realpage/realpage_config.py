import os
import json

parameter_store = json.loads(os.environ.get("parameter_store"))
ilm_config = {
    'ws_realpage_ilm_apikey': parameter_store['WS_REALPAGE_ILM_APIKEY'],
    'dh_realpage_ilm_apikey': parameter_store['DH_REALPAGE_ILM_APIKEY'],
    'ws_realpage_l2l_apikey': parameter_store['WS_REALPAGE_L2L_APIKEY'],
    'dh_realpage_l2l_apikey': parameter_store['DH_REALPAGE_L2L_APIKEY'],
    'ilm_host': 'https://api.realpage.com/leasing/lead',
    'environment': parameter_store['CURRENT_ENV'],
}

