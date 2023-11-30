from enum import Enum

class UrlHandler(Enum):
    DEV = "dev"
    QA = "qa"
    STAGE = "stage"
    RC = "rc"
    PROD = "prod"

    # --------------------------------------------------------------------
    # returns [IPS Internal Host] depend of current [stage]
    def get_ips_host(self) -> str:
        if self == UrlHandler.DEV:
            return "https://partner-api.internal.dev.quext.io"
        elif self == UrlHandler.QA:
            return "https://partner-api.internal.dev.quext.io"
        elif self == UrlHandler.STAGE:
            return "https://partner-api.internal.stage.quext.io"
        elif self == UrlHandler.RC:
            return "https://partner-api.internal.stage.quext.io"
        elif self == UrlHandler.PROD:
            return "https://partner-api.internal.prod.quext.io"

    # --------------------------------------------------------------------
    # returns Yardi Host depend of stage
    def get_yardi_host(self) -> str:
        if self == UrlHandler.DEV:
            return ""
        elif self == UrlHandler.QA:
            return ""
        elif self == UrlHandler.STAGE:
            return ""
        elif self == UrlHandler.RC:
            return ""
        elif self == UrlHandler.PROD:
            return ""
        
    # --------------------------------------------------------------------