
class DataController:
    
    def __init__(self, partner, partner_response, errors):
        self.partner_response = partner_response
        self.errors = errors
        self.partner = partner

    def built_response(self):
        print(type(self.partner_response))
        # build proper response structure for every partner
        code = 200 if len(self.errors) == 0 else 502
        response = { 
                    "data": {   
                        "provenance": [ self.partner ],   
                        "residents": self.partner_response  
                        },  
                    "errors": self.errors    
                    }
        print(response)
        print(type(response))
        return code, response