from ExceptionHandling.Utilities.ErrorCode import ErrorCode


class ExceptionBase:
    """ExceptionConstants class contains the
       paramters required for all the Exception
       class"""
    
    error_code: ErrorCode
    error_msg: str
    status_code: int

    def __init__(self,error_code:ErrorCode = None ,error_msg:dict = None, status_code:int = None):
        self.error_code = error_code
        self.status_code = status_code
        if(isinstance(error_msg, dict)):
            self.error_msg = {i:j for i,j in error_msg.items()}
        else:
            self.error_msg = error_msg

class GatewayError(ExceptionBase, Exception):
    """
    GatewayError instantiated when api request failed
    """

    def __init__(self, error_code=None, error_msg=None, status_code=None):        
        super().__init__(error_code, error_msg, status_code)


class DataError(ExceptionBase, Exception):
    """
    DataError instantiated when the input data format is incorrect
    """

    def __init__(self, error_code=None, error_msg=None, status_code=None):    
        super().__init__(error_code, error_msg, status_code)


class ValidationError(ExceptionBase, Exception):
    """
    ValidationError instantiated when the input fails in validation
    """

    def __init__(self, error_code=None, error_msg=None, status_code=None):         
        super().__init__(error_code, error_msg, status_code)


class DateFormatError(ExceptionBase, Exception):
    """
    DateFormatError instantiated when the input date format is incorrect
    """

    def __init__(self, error_code=None, error_msg=None, status_code=None):         
        super().__init__(error_code, error_msg, status_code)


class SecurityGatewayError(ExceptionBase, Exception):
    """
    SecurityGatewayError instantiated when the security json format is incorrect
    """  

    def __init__(self, error_code=None, error_msg=None, status_code=None):         
        super().__init__(error_code, error_msg, status_code)  
        