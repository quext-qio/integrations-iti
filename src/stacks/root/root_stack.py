from aws_cdk import Stack
from constructs import Construct
from src.utils.enums.stage_name import StageName
from src.stacks.shared.env_stack.env_stack import EnvStack
from src.stacks.shared.layers_stack.layers_stack import LayersStack
from src.stacks.shared.api_stack.api_stack import APIStack
from src.stacks.integrations.placepay_stack.placepay_stack import PlacepayStack
from src.stacks.integrations.guestcards_stack.guestcards_stack import GuestcardsStack
from src.stacks.integrations.transunion_stack.transunion_stack import TransUnionStack
from src.stacks.integrations.units_stack.units_stack import UnitsStack
from src.stacks.integrations.communities_stack.communities_stack import CommunitiesStack
from src.stacks.integrations.customers_stack.customers_stack import CustomersStack
from src.stacks.integrations.residents_stack.residents_stack import ResidentsStack
from src.stacks.integrations.engrain_stack.engrain_stack import EngrainStack
from src.stacks.integrations.tour_availability_stack.tour_availability_stack import TourAvailabilityStack
from src.stacks.integrations.conservice_stack.conservice_stack import ConserviceStack

# [RootStack] is the main [Stack] for the project
# It is responsible for load all [NestedStack] and share resources between them
class RootStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, stage: StageName, server_name:str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # --------------------------------------------------------------------
        # [Shared] Env Stack
        # --------------------------------------------------------------------
        # This nestedstack is responsible for load all environment variables 
        # It assume a role to read the secrets from AWS Secrets Manager's shared account
        env_stack = EnvStack(
            self, 
            f"{stage.value}-{server_name}-envStack", 
            stage_name=stage,
            description="Stack load environment variables for all lambda's functions",
        )
        environment=env_stack.get_env


        # --------------------------------------------------------------------
        # [Shared] Layers Stack
        # --------------------------------------------------------------------
        # It nestedstack is responsible for load all layers of project
        # All layers used in lambda's functions should be added here
        #
        # The [shared_layer] is a layer created from all code in [src/utils/shared] folder it is automatically updated every time the project is deployed
        #
        # The [pip_packages_layer] is a layer created from all pip packages in [src/stacks/shared/layers_stack/requirements-all-lambdas.txt] file, 
        # we should add only pip packages used in lambda's functions, for better performance we should keep the environment variable 
        # [PACKAGES] = False by default, and only set it to [PACKAGES] = True when we need to update the pip_packages_layer (development mode), 
        # and also commit the new file [src/utils/layers/pip_packages_layer.zip] to the repository
        layer_stack =  LayersStack(
            self, 
            f"{stage.value}-{server_name}-layerStack",
            description="Stack load all layers to share between lambda's functions", 
        )
        place_api_layer = layer_stack.get_place_api_layer
        mysql_layer = layer_stack.get_mysql_layer
        zeep_layer = layer_stack.get_zeep_layer
        suds_layer = layer_stack.get_suds_layer
        shared_layer = layer_stack.get_shared_layer
        pip_packages_layer = layer_stack.get_pip_packages_layer
        crypto_layer = layer_stack.get_crypto_layer


        # --------------------------------------------------------------------
        # [Shared] API Stack
        # --------------------------------------------------------------------
        # API Gateway for all project
        # It is responsible for load all endpoints of project
        # the value of [get_resources] will return a dictionary with all resources of API Gateway
        api_stack = APIStack(
            self, 
            f"{stage.value}-{server_name}-apiStack", 
            stage=stage,
            description="Stack load API Gateway for all lambda's functions",
        )
        resources = api_stack.get_resources

        
        # Current supported versions of our API
        api_v1 = resources["v1"]
        api_v2 = resources["v2"]

        # API Gateway [V1] resources necessary for NestedStacks
        placepay_resource_v1 = api_v1["placepay"]
        resman_resource_v1 = api_v1["resman"]
        transunion_resource_v1 = api_v1["transunion"]
        general_resource_v1 = api_v1["general"]
        engrain_resource_v1 = api_v1["engrain"]
        

        # API Gateway [V2] resources necessary for NestedStacks
        general_resource_v2 = api_v2["general"]
        tour_resource_v2 = api_v2["tour"]


        # --------------------------------------------------------------------
        # [ENDPOINTS]: It is a group of [NestedStacks] responsibles 
        # for load all endpoints of project, each [NestedStack] will determine 
        # the resources necessary for each endpoint to reduce the size of 
        # resorces loaded in each lambda's function
        # --------------------------------------------------------------------

        # --------------------------------------------------------------------
        # Placepay endpoints
        # --------------------------------------------------------------------
        PlacepayStack(
            self,
            f"{stage.value}-{server_name}-placepayStack",
            description="Stack for placepay endpoints",
            api=placepay_resource_v1,
            environment=environment,
            layers=[
                place_api_layer,
                shared_layer,
                pip_packages_layer,
            ],
        )
        
        
        # --------------------------------------------------------------------
        # Guestcards endpoints
        # --------------------------------------------------------------------
        GuestcardsStack(
            self, 
            f"{stage.value}-{server_name}-guestcardsStack", 
            description="Stack for guestcards endpoints",
            api=general_resource_v2,
            environment=environment,
            layers=[
                pip_packages_layer,
                shared_layer,
            ],
        )

        # --------------------------------------------------------------------
        # Transunion endpoints
        # --------------------------------------------------------------------
        TransUnionStack(
            self, 
            f"{stage.value}-{server_name}-transUnionStack", 
            api=transunion_resource_v1, 
            environment=environment,
            description="Stack for transunion endpoints",
            layers=[
                pip_packages_layer,
                shared_layer,
            ],
        )

        # --------------------------------------------------------------------
        # Units endpoints
        # --------------------------------------------------------------------
        UnitsStack(
            self, 
            f"{stage.value}-{server_name}-unitsStack", 
            api=general_resource_v2, 
            environment=environment,
            description="Stack for units endpoints",
            layers=[
                pip_packages_layer, 
                mysql_layer, 
                zeep_layer, 
                suds_layer, 
                shared_layer,
            ],
        )

        # --------------------------------------------------------------------
        # Communities endpoints
        # --------------------------------------------------------------------
        CommunitiesStack(
            self, 
            f"{stage.value}-{server_name}-communitiesStack", 
            api=general_resource_v1, 
            description="Stack for communities endpoints",
            layers=[
                pip_packages_layer,
                shared_layer,
            ],
            environment=environment,
        )

        # --------------------------------------------------------------------
        # Customers endpoints
        # --------------------------------------------------------------------
        CustomersStack(
            self, 
            f"{stage.value}-{server_name}-customersStack", 
            api=general_resource_v1, 
            description="Stack for customers endpoints",
            layers=[
                pip_packages_layer,
                shared_layer,
            ],
            environment=environment,
        )

        # --------------------------------------------------------------------
        # Residents endpoints
        # --------------------------------------------------------------------
        ResidentsStack(
            self, 
            f"{stage.value}-{server_name}-residentsStack", 
            api=general_resource_v1, 
            description="Stack for residents endpoints",
            layers=[
                pip_packages_layer,
                shared_layer,
                crypto_layer,
                mysql_layer,
            ],
            environment=environment,
        )

        # --------------------------------------------------------------------
        # Engrain Job and endpoints
        # --------------------------------------------------------------------
        EngrainStack(
            self, 
            f"{stage.value}-{server_name}-engrainStack",
            environment=environment,
            description="Stack for Engrain Job",
            api=engrain_resource_v1,
            layers=[
                mysql_layer,
                pip_packages_layer,
                shared_layer,
            ],
        )

        # --------------------------------------------------------------------
        # Tours endpoints
        # --------------------------------------------------------------------
        TourAvailabilityStack(
            self, 
            f"{stage.value}-{server_name}-tourAvailabilityStack",
            api=tour_resource_v2, 
            layers=[
                pip_packages_layer,
                suds_layer,
                shared_layer
            ],
            environment=environment,
            description="Stack for Tour availability endpoints",
        )

        # --------------------------------------------------------------------
        # Conservice endpoints
        # --------------------------------------------------------------------
        ConserviceStack(
            self, 
            f"{stage.value}-{server_name}-conserviceStack", 
            api=general_resource_v1, 
            environment=environment,
            description="Stack for conservice endpoints",
            layers=[
                pip_packages_layer,
                shared_layer,
            ]
        )



