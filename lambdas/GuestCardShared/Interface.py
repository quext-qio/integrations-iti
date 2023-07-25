from GuestCardShared.DataValidation import BaseGuestCardData


class Interface:
    Body: {}
    Params: {}
    Headers: {}
    Error: {}

    def getOutgoingChannelData(self, appointment_data: BaseGuestCardData, platform_data: dict):
        pass

    def formatOutgoingChannelResponse(self, _data: dict):
        pass
