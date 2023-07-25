import abc

class IConverter(abc.ABC):
    @abc.abstractmethod
    def xml_to_dict(self, xml):
        """From xml to dict"""

    @abc.abstractmethod
    def json_to_dict(self, json_obj):
        """From json to dict"""

    @abc.abstractmethod
    def xml_to_json(self):
        """From xml to json"""

    @abc.abstractmethod
    def json_to_xml(self):
        """From json to xml"""

    @abc.abstractmethod
    def result(self):
        """Get result"""