import os, zipfile, shutil
from constructs import Construct
from aws_cdk import (
    NestedStack,
    aws_lambda as lambda_,
)
from src.utils.enums.app_environment import AppEnvironment

class LayersStack(NestedStack):
    @property
    def get_place_api_layer(self):
        return self.place_api_layer

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
    
    @property
    def get_pip_packages_layer(self):
        return self.pip_packages_layer
    
    @property
    def get_crypto_layer(self):
        return self.crypto_layer
    
    @property
    def get_salesforce_layer(self):
        return self.salesforce_layer
    
    @property
    def get_jira_layer(self):
        return self.jira_layer
    
    def __init__(self, scope: Construct, construct_id: str, app_environment: AppEnvironment, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # --------------------------------------------------------------------
        # Create a layer called [shared_layer] in complilation time
        self.create_shared_layer()

        # Setting the environment variable PACKAGES to True will 
        # re-create the package for [pip_packages_layer]
        should_create_dynamic_packages = os.getenv('PACKAGES', False)

        if str(should_create_dynamic_packages) == "True":
            # Create a layer with all the pip packages defined in [requirements-all-lambdas.txt]
            self.create_pip_packages_as_layer_zip()

        # --------------------------------------------------------------------
        # Create place-api layer
        place_api_layer = lambda_.LayerVersion(
            self, f"{app_environment.get_stage_name()}-place-api-layer",
            layer_version_name=f"{app_environment.get_stage_name()}-place-api-layer",
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
        # Create mysql_layer layer
        mysql_layer = lambda_.LayerVersion(
            self, f"{app_environment.get_stage_name()}-mysql-layer",
            layer_version_name=f"{app_environment.get_stage_name()}-mysql-layer",
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
        # Create zeep_layer layer
        zeep_layer = lambda_.LayerVersion(
            self, f"{app_environment.get_stage_name()}-zeep-layer",
            layer_version_name=f"{app_environment.get_stage_name()}-zeep-layer",
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
        # Create suds_layer layer
        suds_layer = lambda_.LayerVersion(
            self, f"{app_environment.get_stage_name()}-sudspy3-layer",
            layer_version_name=f"{app_environment.get_stage_name()}-sudspy3-layer",
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
        # Create suds_layer layer
        crypto_layer = lambda_.LayerVersion(
            self, f"{app_environment.get_stage_name()}-cryptodome-layer",
            layer_version_name=f"{app_environment.get_stage_name()}-cryptodome-layer",
            description="Package documentation: https://pypi.org/project/",
            code=lambda_.Code.from_asset("./src/utils/layers/crypto_layer.zip"),
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
        self.crypto_layer = crypto_layer  

        # --------------------------------------------------------------------
        # Salesforce Layer 
        salesforce_layer = lambda_.LayerVersion(
            self, f"{app_environment.get_stage_name()}-salesforce-layer",
            layer_version_name=f"{app_environment.get_stage_name()}-salesforce-layer",
            description="Package documentation: https://pypi.org/project/simple-salesforce/",
            code=lambda_.Code.from_asset("./src/utils/layers/salesforce_layer.zip"),
            compatible_runtimes=[
                lambda_.Runtime.PYTHON_3_8,
                lambda_.Runtime.PYTHON_3_7,
                lambda_.Runtime.PYTHON_3_6,
            ],
            compatible_architectures=[
                lambda_.Architecture.ARM_64,
                lambda_.Architecture.X86_64,
            ],
        )
        self.salesforce_layer = salesforce_layer  

        # --------------------------------------------------------------------
        # Jira Layer 
        jira_layer = lambda_.LayerVersion(
            self, f"{app_environment.get_stage_name()}-jira-layer",
            layer_version_name=f"{app_environment.get_stage_name()}-jira-layer",
            description="Package documentation: https://pypi.org/project/jira/",
            code=lambda_.Code.from_asset("./src/utils/layers/jira_layer.zip"),
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
        self.jira_layer = jira_layer  

        # --------------------------------------------------------------------
        # Create Custom Shared Layer 
        shared_layer = lambda_.LayerVersion(
            self, f"{app_environment.get_stage_name()}-custom-shared-layer",
            layer_version_name=f"{app_environment.get_stage_name()}-custom-shared-layer",
            description="Shared layer generated by code in [Integrations-iti] repository in next folder (src/utils/shared), this layer is generated in complilation time",
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
        # Pip Packages Layer 
        pip_packages_layer = lambda_.LayerVersion(
            self, f"{app_environment.get_stage_name()}-integration-pip-packages-layer",
            layer_version_name=f"{app_environment.get_stage_name()}-integration-pip-packages-layer",
            description="Custom layer generated by code in [Integrations-iti] repository to share pip packages in all lambda functions, this layer is generated in complilation time", 
            code=lambda_.Code.from_asset("./src/utils/layers/pip_packages_layer.zip"),
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
        self.pip_packages_layer = pip_packages_layer  


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

    
    # --------------------------------------------------------------------
    # Method to create [pip_packages_layer.zip] 
    # with all the packages in [requirements-all-lambdas.txt]
    def create_pip_packages_as_layer_zip(self):
        os.makedirs("folder", exist_ok=True)
        print("=> Directory 'folder' created")

        # Change to the newly created directory
        os.chdir("folder")

        # Create virtual environment "v-env"
        os.system(f"virtualenv {os.getcwd()}/v-env")
        print("=> Virtual environment 'v-env' created")

        # Activate the virtual environment "v-env"
        #os.system(f"source {os.getcwd()}/v-env/bin/activate")
        venv_path = os.path.join(os.getcwd(), "v-env", "bin", "activate_this.py")
        exec(open(venv_path).read(), {"__file__": venv_path})
        print("=> Virtual environment 'v-env' activated")

        # Read values from requirements-all-lambdas.txt
        base_dir = os.getcwd().replace("folder", "")
        requirements_file = os.path.join(base_dir, "src/stacks/shared/layers_stack/requirements-all-lambdas.txt")
        with open(requirements_file, "r") as file:
            packages = [line.strip() for line in file.readlines()]

        # Install all the Python libraries specified by package_name inside the virtual environment "v-env"
        for package_name in packages:
            print(f"=> Installing {package_name}")
            os.system(f"pip install {package_name}")

        # Deactivate the virtual environment "v-env"
        os.system(f"exit")
        print("=> Virtual environment 'v-env' deactivated")

        # Get Python version
        version_info = os.popen("python --version").read().strip()
        python_version_info = version_info.split(" ")[1].split(".")[:2]
        python_version = f"{python_version_info[0]}.{python_version_info[1]}"
        print(f"=> Python version: {python_version}")

        # Create a new directory called "python"
        os.makedirs("python", exist_ok=True)
        print("=> Directory 'python' created")

        # Copy all files and folders from the "site-packages" directory inside the "v-env" virtual environment
        os.system(f"cp -r {os.getcwd()}/v-env/lib/python{python_version}/site-packages/* {os.getcwd()}/python")
        print("=> All files and folders from the 'site-packages' directory inside the 'v-env' virtual environment copied to 'python' directory")

        # Zip the "python" directory
        os.system(f"zip -r {os.getcwd().replace('folder', '')}src/utils/layers/pip_packages_layer.zip python")
        print("=> pip_packages_layer.zip created")

        # Change back to the original directory and delete the "folder" directory
        os.chdir("..")
        shutil.rmtree("folder")
        print("=> Directory 'folder' deleted")