from ApplicantScreeningShared.DataValidation import BaseApplicationScreeningData, BaseApplicationRetrievalData


class IntegrationInterface:
    Body: {}
    Params: {}
    Headers: {}
    Error: {}

    def getApplicantScreeningRequestData(self, applicationData: BaseApplicationScreeningData, platformData: dict):
        pass

    def formatApplicantScreeningResponse(self, _data: dict):
        pass

    def getApplicantRetrievalRequestData(self, applicationData: BaseApplicationRetrievalData, platformData: dict):
        pass

    def formatApplicationRetrievalResponse(self, _data: dict):
        pass
