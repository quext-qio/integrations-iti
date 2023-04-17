from enum import Enum

from DataPushPullShared.MarketData.Platform.NewCoPlatform import NewCoPlatform
from DataPushPullShared.MarketData.Platform.RentDynamicsPlatform import RentDynamicsPlatform


class PlatformType(Enum):
    NONE = 0
    NEWCO = 1
    RENTDYNAMICS = 2


class Routing:
    @staticmethod
    def get_platform_type(_type: str):
        """
            @desc: this method will check for the _type value and returns the platform type
            @param: _type string which contains platform name (eg: NESTIO, PERIODIC)
            @return: platform type enum value
        """
        switcher = {
            'NEWCO': PlatformType.NEWCO,
            'RENTDYNAMICS': PlatformType.RENTDYNAMICS
        }
        return switcher.get(_type, PlatformType.NONE)

    @staticmethod
    def get_platform_object(_type: PlatformType):
        """
            @desc: this method will check for the _type value and returns the platform object
            @param: _type enum value of the platform (eg: Platform_Type.RentDynamics, Platform_Type.NewCo)
            @return: platform object
        """
        switcher = {
            PlatformType.NEWCO: NewCoPlatform,
            PlatformType.RENTDYNAMICS: RentDynamicsPlatform
        }
        return switcher.get(_type)
