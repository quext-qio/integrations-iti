from abc import ABC, abstractmethod


class ServiceInterface(ABC):
    @abstractmethod
    def get_guest_card_data(self, request_data):
        pass
