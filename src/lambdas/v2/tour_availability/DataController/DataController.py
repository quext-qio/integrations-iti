from datetime import datetime
import pytz

class DataController:
    def __init__(self, errors):
        self.errors = errors

    def built_response(self, data):
        code = 502 if self.errors else 200
        # build proper response structure for every partner
        
        # Set the time zone to Central Standard Time (CST)
        cst_timezone = pytz.timezone('America/Chicago')

        # Get the current time in CST
        current_time = datetime.now(cst_timezone).strftime("%Y-%m-%d %H:%M:%S")
        
        # Filter dates greater than or equal to the current time
        available_dates = [date for date in data["data"]["availableTimes"] if date >= current_time]


        response = { 
            "data": {   
                "availableTimes": available_dates   
            },  
            "error": self.errors    
        }
        return code, response
