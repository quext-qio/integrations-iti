import inspect
import traceback
import logging
import sys
import os

class ZatoConsoleLogger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        # Custom formatter
        formatter = logging.Formatter("%(asctime)s - Log-Level:%(levelno)d - %(levelname)s - %(name)s - %(thread)d:%(threadName)s-%(process)d - %(message)s")
        # Custom handler that writes to the console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        # Remove existing handlers from the logger
        self.handlers = []
        # Add the custom handler to the logger
        self.addHandler(console_handler)
        # Set the logging level for the logger
        # self.setLevel(logging.INFO)
        self.setLevel(os.getenv("LEVEL", 'INFO'))

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):        
        traceback_info = traceback.extract_stack()[-3]
        line_no = str(traceback_info.lineno)
        filename = traceback_info.filename.split('/')[-1]
        fname = traceback_info.name
        message = filename+":"+line_no+" in "+fname+ " "+ str(msg)
        if logging._levelToName.get(level) == 'ERROR':
            exc_info = True
        super()._log(level, message, args, exc_info, extra)

# Get the Zato logger
logger = ZatoConsoleLogger("Integration")

