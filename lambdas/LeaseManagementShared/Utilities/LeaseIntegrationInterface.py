class PlatformInterface:
    Body: {}
    Params: {}
    Headers: {}
    Error: {}

    def createLeaseRequestData(self, leaseData: dict, platformData: dict, tokenData: dict, paramsData: dict = None):
        pass

    def updateLeaseRequestData(self, leaseData: dict, platformData: dict, tokenData: dict, paramsData: dict):
        pass

    def getAuthorizationData(self, platformData: dict, cacheData: dict = None):
        pass

    def formatCreateLeaseResponseData(self, _data: dict):
        pass

    def formatUpdateLeaseResponseData(self, _data: dict):
        pass
