class DataController:
    def __init__(self, errors):
        self.errors = errors

    def built_response(self, data):
        # build proper response structure for every partner
        code = 502 if self.errors else 200
        response = { 
            "data": {   
                "availableTimes": data   
            },  
            "error": self.errors    
        }
        return code, response
