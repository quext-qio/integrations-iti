import os
import json

parameter_store = json.loads(os.environ.get("parameter_store"))
config = {
    "Funnel_api_key": parameter_store['FUNNEL_API_KEY'],
    "Quext_calendar_host": parameter_store['QXT_CALENDAR_TOUR_HOST']
} 