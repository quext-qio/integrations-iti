from urllib.parse import urlencode
import xml.etree.ElementTree as etree

class DataQuext:
    def __init__(self, ips):
        self.ips = ips
        pass

    def get_resident_data(self, credentials):
         return  { "data": { "provenance": [ "quext" ], "residents": [] }, "errors": [] }