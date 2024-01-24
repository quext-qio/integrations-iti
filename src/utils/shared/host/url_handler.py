from enum import Enum


class UrlHandler(Enum):
    DEV = "dev"
    QA = "qa"
    STAGE = "stage"
    RC = "rc"
    PROD = "prod"

    # --------------------------------------------------------------------
    # returns Yardi Host depend of stage
    def get_yardi_host(self) -> str:
        if self == UrlHandler.DEV:
            return "https://www.yardipcv.com/8223tp7s7dev/webservices/itfilsguestcard.asmx"
        elif self == UrlHandler.QA:
            return "https://www.yardipcv.com/8223tp7s7dev/webservices/itfilsguestcard.asmx"
        elif self == UrlHandler.STAGE:
            return "https://www.yardipcv.com/8223tp7s7dev/webservices/itfilsguestcard.asmx"
        elif self == UrlHandler.RC:
            return "https://www.yardipcv.com/8223tp7s7dev/webservices/itfilsguestcard.asmx"
        elif self == UrlHandler.PROD:
            return "https://www.yardipcv.com/8223tp7s7dev/webservices/itfilsguestcard.asmx"
        
    # --------------------------------------------------------------------
    #  returns Auth Host depend of stage
    def get_auth_host(self) -> str:
        if self == UrlHandler.DEV:
            return "https://auth-api.internal.dev.quext.io"
        elif self == UrlHandler.QA:
            return "https://auth-api.internal.dev.quext.io"
        elif self == UrlHandler.STAGE:
            return "https://auth-api.internal.stage.quext.io"
        elif self == UrlHandler.RC:
            return "https://auth-api.internal.stage.quext.io"
        elif self == UrlHandler.PROD:
            return "https://auth-api.internal.prod.quext.io"

    # ------------------------------------------------------------------
    #  returns Leasing Host depend of stage
    def get_leasing_host(self) -> str:
        if self == UrlHandler.DEV:
            return "https://leasing.dev.quext.io"
        elif self == UrlHandler.QA:
            return "https://leasing.dev.quext.io"
        elif self == UrlHandler.STAGE:
            return "https://leasing.stage.quext.io"
        elif self == UrlHandler.RC:
            return "https://leasing.stage.quext.io"
        elif self == UrlHandler.PROD:
            return "https://leasing.stage.quext.io"
