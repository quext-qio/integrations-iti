from aws_cdk import (
    App,
    Stack,
)
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

# [RootStack] is the main stack for the project
# This stack is responsible for load all stacks and share resources between them
class RootStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, stage: StageName, main_app: App, server_name:str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # --------------------------------------------------------------------
        # 1) Env Stack
        # --------------------------------------------------------------------
        # Environment variables for share with all lambda's functions
        env_stack = EnvStack(
            main_app, 
            f"{stage.value}-{server_name}-envStack", 
            stage_name=stage,
            description="Stack load environment variables for all lambda's functions",
        )
        environment=env_stack.get_env
        

        # --------------------------------------------------------------------
        # 2) Layers Stack
        # --------------------------------------------------------------------
        # Load all layers to share between lambda's functions
        layer_stack =  LayersStack(
            main_app, 
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
        # 3) API Stack
        # --------------------------------------------------------------------
        # API Gateway for all project
        api_stack = APIStack(
            main_app, 
            f"{stage.value}-{server_name}-apiStack", 
            stage_name=stage,
            description="Stack load API Gateway for all lambda's functions",
        )
        resources = api_stack.get_resources
        #api = api_stack.get_api
        
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
        # [NestedStack]
        # --------------------------------------------------------------------
        # The purpose of using a NestedStack is to modularize and encapsulate 
        # a specific set of resources within a larger CloudFormation stack. 
        # It promotes modularity, reusability, and scalability by breaking down 
        # complex stacks into smaller components. NestedStacks simplify resource 
        # management, enable independent updates and deletion, and provide 
        # clearer visualization of stack structure and dependencies.
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
            api=resman_resource_v1,
            description="Stack for guestcards endpoints",
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
