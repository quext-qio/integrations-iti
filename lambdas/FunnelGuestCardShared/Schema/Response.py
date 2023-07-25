from asyncio.log import logger


class Response():
    def __init__(self, data, error):
        self.data = data
        self.error = error

    def response(self):
        if "errors" in self.data:
            self.error = self.data["errors"]
            self.data = {} 
        elif  self.error:
            self.error = self.error["error"]
            self.data = {} 
        else:
            self.error = {}
            self.data = self.data["data"]
        return {"data": self.data, "error": self.error}