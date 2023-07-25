from enum import Enum


class ErrorCode(Enum):
    """
    Error Codes Enum
    """
    ERROR_HTTP_0001 = 0
    ERROR_HTTP_0002 = 1
    ERROR_DATA_0001 = 11
    ERROR_INTERNAL_ERROR = 99


class StatusMapper:
    """
    StatusMapper for mapping ErrorCode and Http Status code
    """

    @staticmethod
    def get_status(error_code: ErrorCode):
        """
        Get Http Status code for given error code

        Parameters:
        -----------
        error_code: ErrorCode
            ErrorCode raised during exception

        Return:
        -------
        int
            Http status code
        """
        switcher = {
            ErrorCode.ERROR_HTTP_0001: 400,
            ErrorCode.ERROR_HTTP_0002: 404,
            ErrorCode.ERROR_DATA_0001: 400,
            ErrorCode.ERROR_INTERNAL_ERROR: 500
        }
        return switcher.get(error_code, 400)


class ErrorConstants:
    STATUS_CODE = "status_code"
    ERROR_CODE = "error_code"
    ERROR_MSG = "error_msg"
    INTERNAL_ERROR = "INTERNAL ERROR"
    MESSAGE = "message"
    SECURITY_MSG = "Invalid Security JSON From IPS"
    INVALID_REQUEST  = "Invalid Request body"
    INVALID_DATA = 'Invalid Platform Data'
    

