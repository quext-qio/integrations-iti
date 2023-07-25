# from zato.server.connection.cache import CacheAPI
from zato.server.service import Definition, Outgoing, Request


class Auth:
    """
    Auth Class contains properties like
    Apikey, IntegrationPartnerID, AccountID
    """

    def __init__(self, auth_dict):
        for key in auth_dict:
            setattr(self, key, auth_dict[key])

    def add_property(self, key, value):
        setattr(self, key, value)

    def get_property(self, key):
        return getattr(self, key)

    def pop_property(self, key):
        val = self.get_property(key)
        self.remove_property(key)
        return val

    def remove_property(self, key):
        delattr(self, key)


class ServiceRequest:
    """ ServiceRequest Class contains the required Zato Properties """
    cid: str = None
    request: Request = None
    payload: dict = None
    # cache: CacheAPI = None
    outgoing: Outgoing = None
    purpose = None
    auth: Auth = Auth
    definition: Definition = None
    platformdata: object = None

    def __init__(self, cid: str = None, request: Request = None, payload: dict = None, #cache: CacheAPI = None,
                 outgoing: Outgoing = None, purpose=None, definition: Definition = None):
        self.cid = cid
        self.request = request
        self.payload = payload
        # self.cache = cache
        self.outgoing = outgoing
        self.purpose = purpose
        self.definition = definition
        self.platformdata = None
