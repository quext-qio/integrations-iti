import sys
class DataController:
    
    def __init__(self, errors):
        self.errors = errors

    def built_response(self, data):
        # build proper response structure for every partner
        code = 200 if len(self.errors) == 0 else 502
        response = { 
                    "data": {   
                        "availableTimes": data   
                        },  
                    "errors": self.errors    
                    }
        return code, response
    