from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
)
from constructs import Construct


class LayersStack(Stack):
    @property
    def get_cerberus_layer(self):
        return self.cerberus_layer
    
    @property
    def get_place_api_layer(self):
        return self.place_api_layer
    
    @property
    def get_requests_layer(self):
        return self.requests_layer

    @property
    def get_xmltodict_layer(self):
        return self.xmltodict_layer
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --------------------------------------------------------------------
        # Create cerberus layer
        cerberus_layer = lambda_.LayerVersion(
            self, "CerberusLayer",
            layer_version_name="CerberusLayer",
            description="Package documentation: https://docs.python-cerberus.org/en/stable/",
            code=lambda_.Code.from_asset("src/utils/layers/cerberus_layer.zip"),
            compatible_runtimes=[
                lambda_.Runtime.PYTHON_3_10, 
                lambda_.Runtime.PYTHON_3_9, 
                lambda_.Runtime.PYTHON_3_8, 
                lambda_.Runtime.PYTHON_3_7, 
                lambda_.Runtime.PYTHON_3_6,
            ],
            compatible_architectures=[
                lambda_.Architecture.ARM_64, 
                lambda_.Architecture.X86_64,
            ],
        )
        self.cerberus_layer = cerberus_layer

        # --------------------------------------------------------------------
        # Create place-api layer
        place_api_layer = lambda_.LayerVersion(
            self, "PlaceApiLayer",
            layer_version_name="PlaceApiLayer",
            description="Package documentation: https://pypi.org/project/place-api/",
            code=lambda_.Code.from_asset("./src/utils/layers/place_layer.zip"),
            compatible_runtimes=[
                lambda_.Runtime.PYTHON_3_10, 
                lambda_.Runtime.PYTHON_3_9, 
                lambda_.Runtime.PYTHON_3_8, 
                lambda_.Runtime.PYTHON_3_7, 
                lambda_.Runtime.PYTHON_3_6,
            ],
            compatible_architectures=[
                lambda_.Architecture.ARM_64, 
                lambda_.Architecture.X86_64,
            ],
        )
        self.place_api_layer = place_api_layer

        # --------------------------------------------------------------------
        # Create requests layer
        requests_layer = lambda_.LayerVersion(
            self, "RequestsLayer",
            layer_version_name="RequestsLayer",
            description="Package documentation: https://pypi.org/project/requests/",
            code=lambda_.Code.from_asset("./src/utils/layers/requests_layer.zip"),
            compatible_runtimes=[
                lambda_.Runtime.PYTHON_3_10,
                lambda_.Runtime.PYTHON_3_9,
                lambda_.Runtime.PYTHON_3_8,
                lambda_.Runtime.PYTHON_3_7,
                lambda_.Runtime.PYTHON_3_6,
            ],
            compatible_architectures=[
                lambda_.Architecture.ARM_64,
                lambda_.Architecture.X86_64,
            ],
        )
        self.requests_layer = requests_layer   

        # --------------------------------------------------------------------
        # Create xml to dict layer
        xmltodict_layer = lambda_.LayerVersion(
            self, "XMLToDictLayer",
            layer_version_name="XMLToDictLayer",
            description="Package documentation: https://pypi.org/project/xmltodict/",
            code=lambda_.Code.from_asset("./src/utils/layers/xmltodict_layer.zip"),
            compatible_runtimes=[
                lambda_.Runtime.PYTHON_3_10,
                lambda_.Runtime.PYTHON_3_9,
                lambda_.Runtime.PYTHON_3_8,
                lambda_.Runtime.PYTHON_3_7,
                lambda_.Runtime.PYTHON_3_6,
            ],
            compatible_architectures=[
                lambda_.Architecture.ARM_64,
                lambda_.Architecture.X86_64,
            ],
        )
        self.xmltodict_layer = xmltodict_layer   

        # --------------------------------------------------------------------
