from abc import ABC, abstractmethod

from abc import ABC, abstractmethod


class Controller(ABC):
    """
    Abstract base class defining controller methods.
    """

    @abstractmethod
    def create_guest_card(self, request_data, context):
        """
        Abstract method to create a guest card.

        This method should be implemented by subclasses to handle the creation of a guest card.

        Args:
            request_data (dict): The request data for creating the guest card.
            context: Additional context information.

        Returns:
            Any: The result of creating the guest card.
        """
        pass

