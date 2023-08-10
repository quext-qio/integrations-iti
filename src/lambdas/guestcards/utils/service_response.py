class ServiceResponse:
    def __init__(self, guest_card_id: any, first_name: str, last_name: str, message: any = None, result: str = "SUCCESS", status: str = "NEW", action: str = "INSERT", tour_information: dict = None):
        self.guest_card_id = guest_card_id
        self.first_name = first_name
        self.last_name = last_name
        self.result = result
        self.status = status
        self.action = action
        self.message = message
        self.tour_information = tour_information
        
    def format_response(self):
        return {
            "guestCardInformation": {
                "guestCardId": self.guest_card_id,
                "message": self.message,
                "firstName": self.first_name,
                "lastName": self.last_name,
                "result": self.result,
                "status": self.status,
                "action": self.action,
            },
            "tourInformation": self.tour_information
        }