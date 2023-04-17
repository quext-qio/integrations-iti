import time
from abc import ABCMeta, abstractmethod
from enum import Enum

import jwt

from PeriodicShared.Utilities.Convert import Struct


class IBuilder(metaclass=ABCMeta):
    """The Builder Interface"""

    @staticmethod
    @abstractmethod
    def build_create_provider():
        """Build create provider"""

    @staticmethod
    @abstractmethod
    def build_get_provider():
        """Build get provider"""

    @staticmethod
    @abstractmethod
    def build_get_resource():
        """Build get resource"""

    @staticmethod
    @abstractmethod
    def build_update_bookable():
        """Build update bookable"""

    @staticmethod
    @abstractmethod
    def build_update_resource():
        """Build update resource"""

    @staticmethod
    @abstractmethod
    def build_delete_resource():
        """Build delete resource"""

    @staticmethod
    @abstractmethod
    def build_delete_provider():
        """Build delete provider"""

    @staticmethod
    @abstractmethod
    def build_delete_bookable():
        """Build delete bookable"""

    @staticmethod
    @abstractmethod
    def build_get_bookable():
        """Build get bookable"""

    @staticmethod
    @abstractmethod
    def build_create_bookable():
        """Build part create bookable"""

    @staticmethod
    @abstractmethod
    def build_create_resource():
        """Build part create resource"""

    @staticmethod
    @abstractmethod
    def build_name():
        """Build part name"""

    @staticmethod
    @abstractmethod
    def build_subdomain():
        """Build part subdomain"""

    @staticmethod
    @abstractmethod
    def build_email():
        """Build part email"""

    @staticmethod
    @abstractmethod
    def build_address():
        """Build part address"""

    @staticmethod
    @abstractmethod
    def build_phone():
        """Build part phone"""

    @staticmethod
    @abstractmethod
    def build_sms_source():
        """Build part sms_source"""

    @staticmethod
    @abstractmethod
    def build_loginenabled():
        """Build part loginenabled"""

    @staticmethod
    @abstractmethod
    def build_notificationsenabled():
        """Build part notificationenabled"""

    @staticmethod
    @abstractmethod
    def build_requirelogin():
        """Build part requiredlogin"""

    @staticmethod
    @abstractmethod
    def build_state():
        """Build part state"""

    @staticmethod
    @abstractmethod
    def build_timezone():
        """Build part timezone"""

    @staticmethod
    @abstractmethod
    def build_zip():
        """Build part zip"""

    @staticmethod
    @abstractmethod
    def build_website():
        """Build part website"""

    @staticmethod
    @abstractmethod
    def build_country():
        """Build part country"""

    @staticmethod
    @abstractmethod
    def build_city():
        """Build part city"""

    @staticmethod
    @abstractmethod
    def build_unitofmessurement():
        """Build part unitofmessurement"""

    @staticmethod
    @abstractmethod
    def build_facebook():
        """Build part facebook"""

    @staticmethod
    @abstractmethod
    def build_twitter():
        """Build part twitter"""

    @staticmethod
    @abstractmethod
    def build_instagram():
        """Build part instagram"""

    @staticmethod
    @abstractmethod
    def build_pintrest():
        """Build part pintrest"""

    @staticmethod
    @abstractmethod
    def build_replyto():
        """Build part replyto"""

    @staticmethod
    @abstractmethod
    def build_internal_code():
        """Build part internal_code"""

    @staticmethod
    @abstractmethod
    def build_description():
        """Build part description"""

    @staticmethod
    @abstractmethod
    def obj():
        """Return the periodic object"""

    @staticmethod
    @abstractmethod
    def build_provider():
        """Build part provider"""

    @staticmethod
    @abstractmethod
    def build_seats():
        """Build part seats"""

    @staticmethod
    @abstractmethod
    def build_newavailability():
        """Build part newavailability"""

    @staticmethod
    @abstractmethod
    def build_active():
        """Build part active"""

    @staticmethod
    @abstractmethod
    def build_duration():
        """Build part duration"""

    @staticmethod
    @abstractmethod
    def build_capacity_mode():
        """Build part capacity_mode"""

    @staticmethod
    @abstractmethod
    def build_phonenumber():
        """Build part phonenumber"""

    @staticmethod
    @abstractmethod
    def build_reservation_capacity():
        """Build part reservation_capacity"""

    @staticmethod
    @abstractmethod
    def build_frequency():
        """Build part frequency"""

    @staticmethod
    @abstractmethod
    def build_requiredresources():
        """Build part requiredresources"""

    @staticmethod
    @abstractmethod
    def build_value_capacity():
        """Build part value_capacity"""

    @staticmethod
    @abstractmethod
    def build_update_bookable():
        """Build part update bookable"""

    @staticmethod
    @abstractmethod
    def build_url():
        """Build part url"""

    @staticmethod
    @abstractmethod
    def build_recipients():
        """Build part recipients"""

    @staticmethod
    @abstractmethod
    def build_allowcustomerinvitations():
        """Build part allowcustomerinvitations"""

    @staticmethod
    @abstractmethod
    def build_type():
        """Build part type"""

    @staticmethod
    @abstractmethod
    def build_interval():
        """Build part interval"""

    @staticmethod
    @abstractmethod
    def build_sender():
        """Build part sender"""

    @staticmethod
    @abstractmethod
    def build_forms():
        """Build part forms"""

    @staticmethod
    @abstractmethod
    def build_whitelabel():
        """Build part whitelabel"""

    @staticmethod
    @abstractmethod
    def build_messagetype():
        """Build part messagetype"""

    @staticmethod
    @abstractmethod
    def build_id():
        """Build part id"""

    @staticmethod
    @abstractmethod
    def build_trigger():
        """Build part name"""

    @staticmethod
    @abstractmethod
    def build_providerids():
        """Build part providerids"""

    @staticmethod
    @abstractmethod
    def build_template():
        """Build part template"""

    @staticmethod
    @abstractmethod
    def build_providers():
        """Build part providers"""

    @staticmethod
    @abstractmethod
    def build_businesshours():
        """Build part businesshours"""

    @staticmethod
    @abstractmethod
    def build_bookable_id():
        """Build part bookable_id"""

    @staticmethod
    @abstractmethod
    def build_refundcutoff():
        """Build part refundcutoff"""

    @staticmethod
    @abstractmethod
    def build_messagenotifications():
        """Build part messagenotifications"""

    @staticmethod
    @abstractmethod
    def build_create_message_notification():
        """Build part messagenotifications"""


class Builder(IBuilder):
    """The Concrete Builder."""

    def __init__(self):
        self.periodic = PeriodicPayload()

    def obj(self):
        self.periodic.params = Struct(**self.periodic.params)
        return self.periodic

    def build_create_provider(self):
        self.periodic.method = "create_provider"
        return self

    def build_get_provider(self):
        self.periodic.method = "get_provider"
        return self

    def build_get_resource(self):
        self.periodic.method = "get_resources_for_provider"
        return self

    def build_get_bookable(self):
        self.periodic.method = "get_bookables_for_provider"
        return self

    def build_create_bookable(self):
        self.periodic.method = "create_bookable"
        return self

    def build_create_resource(self):
        self.periodic.method = "create_resource"
        return self

    def build_template(self):
        self.periodic.params["template"] = ""
        return self

    def build_name(self):
        self.periodic.params["name"] = ""
        return self

    def build_update_bookable(self):
        self.periodic.method = "update_bookable"
        return self

    def build_update_provider(self):
        self.periodic.method = "update_provider"
        return self

    def build_update_resource(self):
        self.periodic.method = "update_resource"
        return self

    def build_delete_resource(self):
        self.periodic.method = "delete_resource"
        return self

    def build_delete_provider(self):
        self.periodic.method = "delete_provider"
        return self

    def build_delete_bookable(self):
        self.periodic.method = "delete_bookable"
        return self

    def build_subdomain(self):
        self.periodic.params["subdomain"] = ""
        return self

    def build_email(self):
        self.periodic.params["email"] = ""
        return self

    def build_address(self):
        self.periodic.params["address"] = ""
        return self

    def build_interval(self):
        self.periodic.params["interval"] = {
            "quantity": 0,
            "unit": ""
        }
        return self

    def build_phone(self):
        self.periodic.params["phone"] = ""
        return self

    def build_loginenabled(self):
        self.periodic.params["loginenabled"] = False
        return self

    def build_notificationsenabled(self):
        self.periodic.params["notificationsenabled"] = False
        return self

    def build_requirelogin(self):
        self.periodic.params["requirelogin"] = False
        return self

    def build_state(self):
        self.periodic.params["state"] = ""
        return self

    def build_timezone(self):
        self.periodic.params["timezone"] = ""
        return self

    def build_zip(self):
        self.periodic.params["zip"] = ""
        return self

    def build_website(self):
        self.periodic.params["website"] = ""
        return self

    def build_country(self):
        self.periodic.params["country"] = ""
        return self

    def build_city(self):
        self.periodic.params["city"] = ""
        return self

    def build_unitofmessurement(self):
        self.periodic.params["unitofmessurement"] = ""
        return self

    def build_facebook(self):
        self.periodic.params["facebook"] = ""
        return self

    def build_twitter(self):
        self.periodic.params["twitters"] = ""
        return self

    def build_bookable_id(self):
        self.periodic.params["bookable_id"] = ""
        return self

    def build_instagram(self):
        self.periodic.params["instagram"] = ""
        return self

    def build_pintrest(self):
        self.periodic.params["pintrest"] = ""
        return self

    def build_trigger(self):
        self.periodic.params["trigger"] = "booking"
        return self

    def build_refundcutoff(self):
        self.periodic.params["refundcutoff"] = 24
        return self

    def build_replyto(self):
        self.periodic.params["replyto"] = ""
        return self

    def build_internal_code(self):
        self.periodic.params["internal_code"] = ""
        return self

    def build_id(self):
        self.periodic.params["id"] = ""
        return self

    def build_sender(self):
        self.periodic.params["sender"] = ""
        return self

    def build_description(self):
        self.periodic.params["description"] = ""
        return self

    def build_provider(self):
        self.periodic.params["provider"] = ""
        return self

    def build_recipients(self):
        self.periodic.params["recipients"] = [
            "customer",
            "resourceuser"
        ]
        return self

    def build_seats(self):
        self.periodic.params["seats"] = ""
        return self

    def build_newavailability(self):
        self.periodic.params["newavailability"] = []
        return self

    def build_active(self):
        self.periodic.params["active"] = True
        return self

    def build_capacity_mode(self):
        self.periodic.params["capacity_mode"] = ""
        return self

    def build_phonenumber(self):
        self.periodic.params["phonenumber"] = ""
        return self

    def build_reservation_capacity(self):
        self.periodic.params["reservation_capacity"] = 1
        return self

    def build_messagetype(self):
        self.periodic.params["messagetype"] = ""
        return self

    def build_value_capacity(self):
        self.periodic.params["value_capacity"] = 0
        return self

    def build_url(self):
        self.periodic.params["url"] = ""
        return self

    def build_allowcustomerinvitations(self):
        self.periodic.params["allowcustomerinvitations"] = False
        return self

    def build_forms(self):
        self.periodic.params["forms"] = []
        return self

    def build_type(self):
        self.periodic.params["type"] = "resource"
        return self

    def build_messagenotifications(self):
        self.periodic.params["messagenotifications"] = []
        return self

    def build_whitelabel(self):
        self.periodic.params["whitelabel"] = "quextbooking"
        return self

    def build_providerids(self):
        self.periodic.params["providerids"] = []
        return self

    def build_requiredresources(self):
        self.periodic.params["requiredresources"] = []
        return self

    def build_providers(self):
        self.periodic.params["providers"] = []
        return self

    def build_countrycode(self):
        self.periodic.params["build_countrycode"] = "US"
        return self

    def build_frequency(self):
        self.periodic.params["frequency"] = 0
        return self

    def build_duration(self):
        self.periodic.params["duration"] = 0
        return self

    def build_create_message_notification(self):
        self.periodic.method = "create_messagenotification"
        return self

    def build_businesshours(self):
        self.periodic.params["businesshours"] = {
            "monday": [],
            "friday": [],
            "saturday": [],
            "sunday": [],
            "thursday": [],
            "tuesday": [],
            "wednesday": []
        }
        return self

    def build_sms_source(self):
        self.periodic.params["sms_source"] = ""
        return self


class PeriodicPayload:

    def __init__(self):
        self.jsonrpc = "2.0"
        self.method = ""
        self.params = {}
        self.id = "12345"


class Periodic:
    """Periodic Directory to build all API body"""

    URL = "https://admin.quextbooking.com/rpc"

    @staticmethod
    def getEntity(_type: str):
        switcher = {
            'COMMUNITY': Entity.COMMUNITY,
            'RESOURCE': Entity.RESOURCE,
            'BOOKABLE': Entity.BOOKABLE,
            'MESSAGE': Entity.MESSAGE
        }
        return switcher.get(_type.upper(), Entity.NONE)

    @staticmethod
    def token(issuer, subject, key):
        """Constructs JWT token for authorization headers"""
        return 'Bearer {}'.format(
            jwt.encode(
                {'iat': int(time.time()),
                 'iss': issuer,
                 'sub': subject},
                key, algorithm='HS256').decode('UTF-8')
        )

    @staticmethod
    def createProvider():
        """Constructs and returns the final Create Provider API body"""
        return Builder() \
            .build_create_provider() \
            .build_name() \
            .build_subdomain() \
            .build_email() \
            .build_address() \
            .build_loginenabled() \
            .build_notificationsenabled() \
            .build_requirelogin() \
            .build_state() \
            .build_timezone() \
            .build_zip() \
            .build_website() \
            .build_country() \
            .build_city() \
            .build_unitofmessurement() \
            .build_facebook() \
            .build_twitter() \
            .build_instagram() \
            .build_pintrest() \
            .build_replyto() \
            .build_internal_code() \
            .build_description() \
            .build_phone() \
            .build_countrycode() \
            .build_businesshours() \
            .build_sms_source() \
            .obj()

    @staticmethod
    def createBookable():
        """Constructs and returns the final Create Bookable API body"""
        return Builder() \
            .build_create_bookable() \
            .build_name() \
            .build_provider() \
            .build_newavailability() \
            .build_frequency() \
            .build_duration() \
            .build_whitelabel() \
            .build_requiredresources() \
            .build_forms() \
            .build_refundcutoff() \
            .build_messagenotifications() \
            .obj()

    @staticmethod
    def createResource():
        """Constructs and returns the final Create Resource API body"""
        return Builder() \
            .build_create_resource() \
            .build_newavailability() \
            .build_description() \
            .build_countrycode() \
            .build_name() \
            .build_phonenumber() \
            .build_reservation_capacity() \
            .build_timezone() \
            .build_url() \
            .build_whitelabel() \
            .build_providers() \
            .build_providerids() \
            .obj()

    @staticmethod
    def createMessageNotification():
        """Constructs and returns the final Create Message Notification API body"""
        return Builder() \
            .build_create_message_notification() \
            .build_messagenotifications() \
            .build_trigger() \
            .build_recipients() \
            .build_sender() \
            .build_interval() \
            .build_template() \
            .build_type() \
            .build_provider() \
            .build_messagetype() \
            .build_bookable_id() \
            .obj()

    @staticmethod
    def createForm(_id):
        """Constructs and returns the form object of type _id"""
        return {
            "display_step": "second_form",
            "form_config_objects": [
                {
                    "form_id": _id,
                    "lock_responses": False,
                    "multiple_submissions": False,
                    "operative": False,
                    "order": 0,
                    "type": "form_config"
                }
            ],
            "name": "",
            "type": "form_group"
        }

    @staticmethod
    def updateBookable():
        """Constructs and returns the final Update Bookable API body"""
        return Builder() \
            .build_update_bookable() \
            .build_id() \
            .obj()

    @staticmethod
    def updateProvider():
        """Constructs and returns the final Update Provider API body"""
        return Builder() \
            .build_update_provider() \
            .build_subdomain() \
            .obj()

    @staticmethod
    def getProvider():
        """Constructs and returns the final Create Provider API body"""
        return Builder() \
            .build_get_provider() \
            .build_id() \
            .obj()

    @staticmethod
    def getBookable():
        """Constructs and returns the final Create Bookable API body"""
        return Builder() \
            .build_get_bookable() \
            .build_provider() \
            .obj()

    @staticmethod
    def getResource():
        """Constructs and returns the final Create Resource API body"""
        return Builder() \
            .build_get_resource() \
            .build_provider() \
            .obj()

    @staticmethod
    def updateResource():
        """Constructs and returns the final Update Resource API body"""
        return Builder() \
            .build_update_resource() \
            .build_id() \
            .obj()

    @staticmethod
    def deleteResource():
        """Constructs and returns the final Delete Resource API body"""
        return Builder() \
            .build_delete_resource() \
            .build_provider() \
            .build_id() \
            .obj()

    @staticmethod
    def deleteProvider():
        """Constructs and returns the final Delete Provider API body"""
        return Builder() \
            .build_delete_provider() \
            .build_id() \
            .obj()

    @staticmethod
    def deleteBookable():
        """Constructs and returns the final Delete Bookable API body"""
        return Builder() \
            .build_delete_bookable() \
            .build_id() \
            .obj()


class EnvironmentType(Enum):
    DEVELOPMENT = 0
    PRODUCTION = 1
    STAGING = 2


class Entity(Enum):
    NONE = ''
    COMMUNITY = 'community'
    RESOURCE = 'resource'
    BOOKABLE = 'bookable'
    MESSAGE = 'message'
