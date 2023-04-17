from TourShared.Model.Data_Model import Platform_Type, Environment_Type
from TourShared.Platform.Funnel_Platform import Funnel_Platform
from TourShared.Platform.Periodic_Platform import Periodic_Platform
from TourShared.Config.Config import periodic_config_development, periodic_config_production, funnel_config_production, \
    funnel_config_development


class Routing:
    @staticmethod
    def get_platform_object(_type: Platform_Type):
        """
            @desc: this method will check for the _type value and returns the platform object
            @param: _type enum value of the platform (eg: Platform_Type.NESTIO, Platform_Type.PERIODIC)
            @return: platform object
        """
        switcher = {
            Platform_Type.FUNNEL: Funnel_Platform,
            Platform_Type.PERIODIC: Periodic_Platform
        }
        return switcher.get(_type)

    @staticmethod
    def get_tour_schedule_outgoing_channel_name(_type: Platform_Type):
        """
            @desc: this method will check for the _type value and returns the outgoing channel definition
            @param: _type enum value of the platform (eg: Platform_Type.NESTIO, Platform_Type.PERIODIC)
            @return: definition of the outgoing channel
        """
        switcher = {
            Platform_Type.FUNNEL: 'Schedule_Nestio_Tour',
            Platform_Type.PERIODIC: 'Schedule_Periodic_Tour'
        }
        return switcher.get(_type)

    @staticmethod
    def get_tour_availability_outgoing_channel_name(_type: Platform_Type):
        """
            @desc: this method will check for the _type value and returns the outgoing channel definition
            @param: _type enum value of the platform (eg: Platform_Type.NESTIO, Platform_Type.PERIODIC)
            @return: definition of the outgoing channel
        """
        switcher = {
            Platform_Type.FUNNEL: 'Get_Available_Times_From_Nestio',
            Platform_Type.PERIODIC: 'Get_Available_Times_From_Periodic'
        }
        return switcher.get(_type, {})

    @staticmethod
    def get_outgoing_request_type(_type: Platform_Type):
        """
            @desc: this method will check for the _type value and returns the outgoing request type definition
            @param: _type enum value of the platform (eg: Platform_Type.NESTIO, Platform_Type.PERIODIC)
            @return: definition of the outgoing request type
        """
        switcher = {
            Platform_Type.FUNNEL: 'GET',
            Platform_Type.PERIODIC: 'POST'
        }
        return switcher.get(_type, {})

    @staticmethod
    def get_platform_config(_type: Platform_Type, _env: Environment_Type):
        """
            @desc: this method will check for the _type value and _env. Return platform config
        """
        if _type == Platform_Type.FUNNEL:
            if _env == Environment_Type.DEVELOPMENT:
                return funnel_config_development
            elif _env == Environment_Type.PRODUCTION:
                return funnel_config_production
        elif _type == Platform_Type.PERIODIC:
            if _env == Environment_Type.DEVELOPMENT:
                return periodic_config_development
            elif _env == Environment_Type.PRODUCTION:
                return periodic_config_production
        return {}
