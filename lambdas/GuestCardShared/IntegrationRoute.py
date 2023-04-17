from enum import Enum

from GuestCardShared.NewCoController import NewCoController


class Platform_Type(Enum):
    NONE = 0
    NEWCO = 1
    FUNNEL = 2


class IntegrationRoute:
    @staticmethod
    def getPlatformType(_type: str):
        switcher = {
            'NEWCO': Platform_Type.NEWCO
        }
        return switcher.get(_type, Platform_Type.NONE)

    @staticmethod
    def getPlatformObject(_type: Platform_Type):
        """
            @desc: this method will check for the _type value and returns the platform object
            @param: _type enum value of the platform (eg: Platform_Type.NEWCO)
            @return: platform object
        """
        switcher = {
            Platform_Type.NEWCO: NewCoController
        }
        return switcher.get(_type, None)

    @staticmethod
    def getOutgoingChannelName(_type: Platform_Type):
        """
            @desc: this method will check for the _type value and returns the outgoing channel definition
            @param: _type enum value of the platform (eg: Platform_Type.NEWCO)
            @return: definition of the outgoing channel
        """
        switcher = {
            Platform_Type.NEWCO: 'Send_GuestCard_To_NewCo',
            Platform_Type.FUNNEL: 'Send_GuestCard_To_NewCo'
        }
        return switcher.get(_type, {})

    @staticmethod
    def getOutgoingRequestType(_type: Platform_Type):
        switcher = {
            Platform_Type.NEWCO: 'POST',
            Platform_Type.FUNNEL: 'POST'
        }
        return switcher.get(_type, {})
