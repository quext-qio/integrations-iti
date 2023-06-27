import sys
class DataController:
    
    def __init__(self, partner, partner_response, errors):
        self.partner_response = partner_response
        self.errors = errors
        self.partner = partner

    def built_response(self):
        # build proper response structure for every partner
        print(sys.path)
        response = { 
                    "data": {   
                        "provenance": [ self.partner ],   
                        "residents": self.partner_response  
                        },  
                    "errors": self.errors    
                    }
        return response