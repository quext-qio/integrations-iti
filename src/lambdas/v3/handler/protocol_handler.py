from src.lambdas.v3.gateway.rest_api_controller import RestAPICaller
from src.lambdas.v3.gateway.soap_api_controller import SOAPCaller


class ProtocolHandler:
    """
    Class for handling protocol-related operations.
    """

    @staticmethod
    def get_protocol(protocol_name):
        """
        Get the protocol caller based on the protocol name.

        Args:
            protocol_name (str): Name of the protocol (e.g., "Rest", "Soap").

        Returns:
            type or None: Protocol caller class if found, otherwise None.
        """
        # Dictionary mapping protocol names to their respective caller classes
        service_gateway = {"rest": RestAPICaller,
                           "soap": SOAPCaller}

        # Check if the protocol name exists in the service_gateway dictionary
        if protocol_name in service_gateway and service_gateway[protocol_name]:
            # Return the caller class corresponding to the protocol name
            return service_gateway[protocol_name]
        # Return None if the protocol name is not found in the dictionary
        return None

