import os
import json


ilm_config = {
    'ws_realpage_ilm_apikey': os.environ['WS_REALPAGE_ILM_APIKEY'],
    'dh_realpage_ilm_apikey': os.environ['DH_REALPAGE_ILM_APIKEY'],
    'spa_realpage_ilm_apikey': os.environ['DH_REALPAGE_ILM_APIKEY'],
    'ws_realpage_l2l_apikey': os.environ['WS_REALPAGE_L2L_APIKEY'],
    'dh_realpage_l2l_apikey': os.environ['DH_REALPAGE_L2L_APIKEY'],
    'spa_realpage_l2l_apikey': os.environ['DH_REALPAGE_L2L_APIKEY'],
    'ilm_host': 'https://api.realpage.com/leasing/lead',
    'environment': os.environ['CURRENT_ENV'],
}

