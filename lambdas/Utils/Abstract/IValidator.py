import abc

class IValidator(abc.ABC):
    @abc.abstractmethod
    def is_valid(self):
        """To Validate Schemas"""