from abc import ABC, abstractmethod


class ServiceInterface(ABC):
    @abstractmethod
    def get_applicant_data(self, request_data):
        pass
