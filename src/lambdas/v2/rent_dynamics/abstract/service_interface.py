from abc import ABC, abstractmethod

class ServiceInterface(ABC):
    @abstractmethod
    def get_data(self, path_parameters: dict, body: dict) -> any:
        pass