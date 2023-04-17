from LeaseManagementShared.Utilities.LeaseIntegrationRoute import PlatformType

configDict = {
    'BLUEMOON': {"cacheDefinition": 'BlueMoon',
                 "cacheType": 'builtin',
                 'url': 'https://api.bluemoonforms.com/oauth/token'}
}


class Config:

    @staticmethod
    def getConfig(_type: PlatformType):
        switcher = {
            PlatformType.BLUEMOON: configDict['BLUEMOON']
        }
        return switcher.get(_type, PlatformType.NONE)
