import zipfile
import os
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
)

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
    
    @property
    def get_mysql_layer(self):
        return self.mysql_layer
    
    @property
    def get_zeep_layer(self):
        return self.zeep_layer
    
    @property
    def get_suds_layer(self):
        return self.suds_layer
    
    @property
    def get_shared_layer(self):
        return self.shared_layer
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Create shared layer in complilation time
        self.create_shared_layer()


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
        # Create mysql_layer layer
        mysql_layer = lambda_.LayerVersion(
            self, "MySQLLayer",
            layer_version_name="MySQLLayer",
            description="Package documentation: https://pypi.org/project/",
            code=lambda_.Code.from_asset("./src/utils/layers/mysql_layer.zip"),
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
        self.mysql_layer = mysql_layer  

         # --------------------------------------------------------------------
        # Create mysql_layer layer
        zeep_layer = lambda_.LayerVersion(
            self, "ZeepLayer",
            layer_version_name="ZeepLayer",
            description="Package documentation: https://pypi.org/project/",
            code=lambda_.Code.from_asset("./src/utils/layers/zeep_layer.zip"),
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
        self.zeep_layer = zeep_layer  

        # --------------------------------------------------------------------
        # Create mysql_layer layer
        suds_layer = lambda_.LayerVersion(
            self, "SudsPy3Layer",
            layer_version_name="SudsPy3Layer",
            description="Package documentation: https://pypi.org/project/",
            code=lambda_.Code.from_asset("./src/utils/layers/suds_layer.zip"),
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
        self.suds_layer = suds_layer  

        # --------------------------------------------------------------------
        # Create Shared Layer
        shared_layer = lambda_.LayerVersion(
            self, "CustomSharedLayer",
            layer_version_name="CustomSharedLayer",
            description="Shared layer generated by code in Integrations-iti repository",
            code=lambda_.Code.from_asset("./src/utils/layers/shared_layer.zip"),
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
        self.shared_layer = shared_layer  


    # --------------------------------------------------------------------
    # Method will create a [shared_layer.zip] file in the [src/utils/layers] folder 
    # with all the files in the shared folder [src/utils/shared]
    def create_shared_layer(self):
        shared_folder = os.path.join(os.getcwd(), 'src/utils/shared')
        output_zip = os.path.join(os.getcwd(), 'src/utils/layers/shared_layer.zip')

        with zipfile.ZipFile(output_zip, 'w') as zipf:
            for root, dirs, files in os.walk(shared_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, shared_folder)
                    zipf.write(file_path, arcname=os.path.join('python', rel_path))

        print(f'Shared layer created in: {output_zip}')



