import abc

class IHeaders(abc.ABC):
    @abc.abstractmethod
    def add(self, key, value):
        """Add new (key:value)"""

    @abc.abstractmethod    
    def remove(self, key):
        """Remove (key:value) by key"""
    
    @abc.abstractmethod
    def remove_all(self):
        """Remove all"""

    @abc.abstractmethod
    def get(self):
        """Returns headers"""