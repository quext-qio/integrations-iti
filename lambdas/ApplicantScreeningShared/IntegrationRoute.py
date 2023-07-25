from enum import Enum

from ApplicantScreeningShared.DataValidation import HTTPRequestType
from ApplicantScreeningShared.TransUnionController import TransUnionController


class PlatformType(Enum):
    NONE = 0
    TRANS_UNION = 1


class IntegrationRoute:
    @staticmethod
    def getPlatformType(_type: str):
        switcher = {
            'TRANSUNION': PlatformType.TRANS_UNION
        }
        return switcher.get(_type, PlatformType.NONE)

    @staticmethod
    def getPlatformObject(_type: PlatformType):
        """
            @desc: this method will check for the _type value and returns the platform object
            @param: _type enum value of the platform (eg: Platform_Type.TRANS_UNION)
            @return: platform object
        """
        switcher = {
            PlatformType.TRANS_UNION: TransUnionController
        }
        return switcher.get(_type, None)

    @staticmethod
    def getCreateApplicationOutgoingChannelName(_type: PlatformType):
        """
            @desc: this method will check for the _type value and returns the outgoing channel definition
            @param: _type enum value of the platform (eg: Platform_Type.NEWCO)
            @return: definition of the outgoing channel
        """
        switcher = {
            PlatformType.TRANS_UNION: 'Create_Application_TransUnion'
        }
        return switcher.get(_type, {})

    @staticmethod
    def getRetrieveApplicationOutgoingChannelName(_type: PlatformType):
        """
            @desc: this method will check for the _type value and returns the outgoing channel definition
            @param: _type enum value of the platform (eg: Platform_Type.NEWCO)
            @return: definition of the outgoing channel
        """
        switcher = {
            PlatformType.TRANS_UNION: 'Retrieve_Application_TransUnion'
        }
        return switcher.get(_type, {})

    @staticmethod
    def getOutgoingRequestType(_type: PlatformType):
        switcher = {
            PlatformType.TRANS_UNION: HTTPRequestType.POST
        }
        return switcher.get(_type, {})
