from Utils.Abstract.IHeaders import IHeaders

class Headers(IHeaders):
  def __init__(self, methods):
    self.headers = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': methods,
      'Access-Control-Allow-Headers': 'Authorization, Content-Type'
    }
  def add(self, key, value):
    self.headers[key] = value
    return self.headers

  def remove(self, key):
    del self.headers[key]
    return self.headers
  
  def remove_all(self):
    self.headers = {}
    return self.headers

  def get(self):
    return self.headers