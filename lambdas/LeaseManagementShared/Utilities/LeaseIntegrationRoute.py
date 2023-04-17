from enum import Enum

from LeaseManagementShared.Controllers.BlueMoonLeaseController import BLUEMOON
from LeaseManagementShared.Utilities.DataValidation import PlatformType


class IntegrationRoute:
    @staticmethod
    def getPlatformType(_type: str):
        switcher = {
            'BLUEMOON': PlatformType.BLUEMOON
        }
        return switcher.get(_type, PlatformType.NONE)

    @staticmethod
    def getPlatformObject(_type: PlatformType):
        """
            @desc: this method will check for the _type value and returns the platform object
            @param: _type enum value of the platform (eg: Platform_Type.BLUEMOON)
            @return: platform object
        """
        switcher = {
            PlatformType.BLUEMOON: BLUEMOON
        }
        return switcher.get(_type)


    @staticmethod
    def securityDefinition(_type: PlatformType):
        switcher = {
            PlatformType.BLUEMOON: True
        }
        return switcher.get(_type, PlatformType.NONE)

    @staticmethod
    def LeaseOutgoingChannelName(_type: PlatformType):
        """
            @desc: this method will check for the _type value and returns the outgoing channel definition
            @param: _type enum value of the platform (eg: PlatformType.BLUEMOON)
            @return: definition of the outgoing channel
        """
        switcher = {
            PlatformType.BLUEMOON: 'Lease_Management_BlueMoon'
        }
        return switcher.get(_type, {})

    @staticmethod
    def LeaseOutgoingDeletelName(_type: PlatformType):
        """
            @desc: this method will check for the _type value and returns the outgoing channel definition
            @param: _type enum value of the platform (eg: PlatformType.BLUEMOON)
            @return: definition of the outgoing channel for delete lease
        """
        switcher = {
            PlatformType.BLUEMOON: 'Lease_Remove_Channel'
        }
        return switcher.get(_type, {})

    @staticmethod
    def LeaseOutgoingPatchlName(_type: PlatformType):
        """
            @desc: this method will check for the _type value and returns the outgoing channel definition
            @param: _type enum value of the platform (eg: PlatformType.BLUEMOON)
            @return: definition of the outgoing channel for update lease
        """
        switcher = {
            PlatformType.BLUEMOON: 'Lease_Update_Channel'
        }
        return switcher.get(_type, {})

    @staticmethod
    def LeaseOutgoingGetlName(_type: PlatformType, param: dict = None):
        """
            @desc: this method will check for the _type value and returns the outgoing channel definition
            @param: _type enum value of the platform (eg: PlatformType.BLUEMOON)
            @return: definition of the outgoing channel for get lease
        """
        if param:
            switcher = {
                PlatformType.BLUEMOON: 'Get_Lease_Channel'
            }
        else:
            switcher = {
                PlatformType.BLUEMOON: 'Get_All_Lease_Channel'
            }

        return switcher.get(_type, {})

    @staticmethod
    def getOutgoingRequestType(_type: PlatformType):
        """
            @desc: this method will check for the _type value and returns the outgoing request type definition
            @param: _type enum value of the platform (eg: Platform_Type.NESTIO, Platform_Type.PERIODIC)
            @return: definition of the outgoing request type
        """
        switcher = {
            PlatformType.BLUEMOON: 'POST'
        }
        return switcher.get(_type, {})
