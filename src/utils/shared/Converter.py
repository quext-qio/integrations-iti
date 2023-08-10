import json
import xmltodict
from collections import OrderedDict
from utils.abstract.IConverter import IConverter

class Converter(IConverter):
  def __init__(self, data):
    self.data = data
    self.response = ""
  
  def xml_to_dict(self, xml):
    return xmltodict.parse(xml)

  def json_to_dict(self, json_obj):
    return json.loads(json_obj, object_pairs_hook=OrderedDict)

  def xml_to_json(self):
    self.response = self.xml_to_dict(self.data)
    return json.dumps(self.response)

  def json_to_xml(self):
    if type(self.data) is not dict:
        response = self.json_to_dict(self.data)
    else:
        response = self.data
    return xmltodict.unparse(response, pretty=True)

  def result(self):
    return self.response

