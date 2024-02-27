from abc import ABC, abstractmethod


class ServiceInterface(ABC):
    @abstractmethod
    def get_quote_for_shopper(self, request_data):
        pass
