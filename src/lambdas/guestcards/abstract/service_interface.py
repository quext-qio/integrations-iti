from abc import ABC, abstractmethod

class ServiceInterface(ABC):
    @abstractmethod
    def get_data(self, body):
        pass