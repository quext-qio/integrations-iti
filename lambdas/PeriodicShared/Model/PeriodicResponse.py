class BaseResponse:
    def __init__(self):
        self.data = {}
        self.error = {}


class Community:
    def __init__(self):
        self.name = ''
        self.id = ''
        self.modified = ''
        self.internalCode = ''
        self.subDomain = ''
        self.phone = ''
        self.email = ''
        self.replyEmail = ''
        self.website = ''
        self.address = ''
        self.state = ''
        self.country = ''
        self.postalCode = ''
        self.facebookURL = ''
        self.twitterURL = ''
        self.instagramURL = ''
        self.pinterestURL = ''
        self.availability = []
        self.timezone = ''
        self.description = ''


class Bookable:
    def __init__(self):
        self.name = ''
        self.id = ''
        self.communityID = ''
        self.modified = ''
        self.appointmentDuration = ''
        self.appointmentFrequency = ''
        self.description = ''
        self.customLink = ''
        self.availability = []


class Resource:
    def __init__(self):
        self.name = ''
        self.id = ''
        self.communityID = ''
        self.modified = ''
        self.availability = []
        self.phone = ''
        self.timezone = ''
        self.url = ''
