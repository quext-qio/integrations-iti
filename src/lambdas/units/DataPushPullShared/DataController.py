import sys
class DataController:
    
    def __init__(self, partner, errors):
        self.errors = errors
        self.partner = partner

    def built_response(self, property_data, models_data, units_data):
        # build proper response structure for every partner
        code = 200 if len(self.errors) == 0 else 502
        response = { 
                    "data": {   
                        "provenance": [ self.partner ],   
                        "property": property_data,
                        "models": models_data,
                        "units": units_data
                        },  
                    "errors": self.errors    
                    }
        return code, response
    