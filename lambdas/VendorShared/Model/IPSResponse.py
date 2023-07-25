from pydantic import BaseModel


class PlatformData(BaseModel):
    communityName: str
    platform: str
    communityID: int
    resmanPropertyID: str


class IPSResponse(BaseModel):
    platformData: dict

class CommunitySet:
    community_id = None
    partner_object = None
    security = {}
    platformdata = {}
    partner_id =None
    partner_name = None

    def __init__(self, community_id :str = None,  partner_object :object = None, partner_id :str = None,
                 platformdata :dict = {}, security: dict = {}, partner_name :str = None):
        self.community_id = community_id
        self.partner_object = partner_object
        self.Partner_id = partner_id
        self.security = security
        self.platformdata = platformdata
        self.partner_name = partner_name

        