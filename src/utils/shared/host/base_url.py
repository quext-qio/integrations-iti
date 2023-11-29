from enum import Enum

class BaseUrl(Enum):
    DEV = "dev"
    QA = "qa"
    STAGE = "stage"
    RC = "rc"
    PROD = "prod"

    # --------------------------------------------------------------------
    # returns IPS Internal Host depend of stage
    def get_ips_host(self) -> str:
        if self == BaseUrl.DEV:
            return "https://partner-api.internal.dev.quext.io"
        elif self == BaseUrl.QA:
            return "https://partner-api.internal.dev.quext.io"
        elif self == BaseUrl.STAGE:
            return "https://partner-api.internal.stage.quext.io"
        elif self == BaseUrl.RC:
            return "https://partner-api.internal.stage.quext.io"
        elif self == BaseUrl.PROD:
            return "https://partner-api.internal.prod.quext.io"

    # --------------------------------------------------------------------
    # returns Yardi Host depend of stage
    def get_yardi_host(self) -> str:
        if self == BaseUrl.DEV:
            return ""
        elif self == BaseUrl.QA:
            return ""
        elif self == BaseUrl.STAGE:
            return ""
        elif self == BaseUrl.RC:
            return ""
        elif self == BaseUrl.PROD:
            return ""
        
    # --------------------------------------------------------------------