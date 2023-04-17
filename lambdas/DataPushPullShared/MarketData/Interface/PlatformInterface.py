import enum


class PlatformInterface:
    Body: {}
    Params: {}
    Headers: {}
    Error: {}

    def getRequestData(self, data, platformData: dict, dataSource: enum = None):
        pass

    def formatResponse(self, data, error):
        pass
