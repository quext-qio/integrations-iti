from ResidentVerificationShared.DataValidation import BaseApplicantData, BaseIdentityEvaluationData


class IntegrationInterface:
    Body: {}
    Params: {}
    Headers: {}
    Error: {}

    def getIdentityVerificationRequestData(self, residentData: BaseApplicantData, platformData: dict):
        pass

    def formatIdentityVerificationResponse(self, _data: dict, _platformData: dict = None):
        pass

    def getIdentityEvaluationRequestData(self, residentData: BaseIdentityEvaluationData, platformData: dict):
        pass

    def formatIdentityEvaluationResponse(self, _data: dict, _platformData: dict = None):
        pass
