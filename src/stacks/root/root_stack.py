import json
from aws_cdk import Stack
from constructs import Construct
from src.utils.enums.app_environment import AppEnvironment
from src.stacks.shared.env_stack.env_stack import EnvStack
from src.stacks.shared.layers_stack.layers_stack import LayersStack
from src.stacks.shared.api_stack.api_stack import APIStack
from src.stacks.shared.vpc_stack.vpc_stack import VpcStack
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
from src.stacks.integrations.salesforce_stack.salesforce_stack import SalesforceStack
from src.stacks.integrations.onetime_link_stack.onetime_link_stack import OneTimeLinkStack
from src.stacks.integrations.rent_dynamics_stack.rent_dynamics_stack import RentDynamicsStack
from src.stacks.integrations.qoops.qoops_stack import QoopsStack
from src.stacks.integrations.trupay_google_stack.trupay_google_stack import TruePayGoogleStack

# [RootStack] is the main [Stack] for the project
# It is responsible for load all [NestedStack] and share resources between them
class RootStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, app_env: AppEnvironment, server_name:str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        # --------------------------------------------------------------------
        # [Shared] Env Stack
        # --------------------------------------------------------------------
        # This nestedstack is responsible for load all environment variables 
        # It assume a role to read the secrets from AWS Secrets Manager's shared account
        env_stack = EnvStack(
            self, 
            f"{app_env.get_stage_name()}-{server_name}-env-stack", 
            app_environment=app_env,
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
            f"{app_env.get_stage_name()}-{server_name}-layer-stack",
            app_environment=app_env,
            description="Stack load all layers to share between lambda's functions", 
        )
        place_api_layer = layer_stack.get_place_api_layer
        mysql_layer = layer_stack.get_mysql_layer
        zeep_layer = layer_stack.get_zeep_layer
        suds_layer = layer_stack.get_suds_layer
        shared_layer = layer_stack.get_shared_layer
        pip_packages_layer = layer_stack.get_pip_packages_layer
        crypto_layer = layer_stack.get_crypto_layer
        salesforce_layer = layer_stack.get_salesforce_layer
        jira_layer = layer_stack.get_jira_layer

        # --------------------------------------------------------------------
        # [Shared] VPC Stack
        # --------------------------------------------------------------------
        vpc_stack = VpcStack(
            self, 
            f"{app_env.get_stage_name()}-{server_name}-vpc-stack",
            app_environment=app_env,
            environment=environment["placepay"],
            layers=[
                shared_layer,
                pip_packages_layer,
            ],
        )
        vpc=vpc_stack.get_vpc
        security_group=vpc_stack.get_security_group
        subnet_selection=vpc_stack.get_subnet_selection



        # --------------------------------------------------------------------
        # [Shared] API Stack
        # --------------------------------------------------------------------
        # API Gateway for all project
        # It is responsible for load all endpoints of project
        # the value of [get_resources] will return a dictionary with all resources of API Gateway
        api_stack = APIStack(
            self, 
            f"{app_env.get_stage_name()}-{server_name}-api-stack", 
            app_environment=app_env,
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
        salesforce_resource_v1 = api_v1["salesforce"]
        rent_dynamics_resource_v1 = api_v1["rentdynamics"]
        

        # API Gateway [V2] resources necessary for NestedStacks
        general_resource_v2 = api_v2["general"]
        tour_resource_v2 = api_v2["tour"]
        jira_resource_v2 = api_v2["jira"]
        salesforce_resource_v2 = api_v2["salesforce"]
        onetime_link_resource_v2 = api_v2["security"]
        rent_dynamics_resource_v2 = api_v2["rentdynamics"]


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
            f"{app_env.get_stage_name()}-{server_name}-placepay-stack",
            app_environment=app_env,
            description="Stack for placepay endpoints",
            api=placepay_resource_v1,
            environment=environment["placepay"],
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
            f"{app_env.get_stage_name()}-{server_name}-guestcards-stack", 
            app_environment=app_env,
            description="Stack for guestcards endpoints",
            api=general_resource_v2,
            environment=environment["guestcards"],
            layers=[
                pip_packages_layer,
                shared_layer,
                suds_layer
            ],
        )

        # --------------------------------------------------------------------
        # Transunion endpoints
        # TODO: Create a swagger for this endpoint
        # --------------------------------------------------------------------
        TransUnionStack(
            self, 
            f"{app_env.get_stage_name()}-{server_name}-trans-union-stack", 
            api=transunion_resource_v1, 
            app_environment=app_env,
            environment=environment["transunion"],
            description="Stack for transunion endpoints",
            layers=[
                pip_packages_layer,
                shared_layer,
            ],
        )

        # --------------------------------------------------------------------
        # Units endpoints
        # TODO: Create a swagger for this endpoint
        # --------------------------------------------------------------------
        UnitsStack(
            self, 
            f"{app_env.get_stage_name()}-{server_name}-units-stack", 
            api=general_resource_v2, 
            app_environment=app_env,
            description="Stack for units endpoints",
            environment=environment["units"],
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
            f"{app_env.get_stage_name()}-{server_name}-communities-stack", 
            api=general_resource_v1, 
            app_environment=app_env,
            description="Stack for communities endpoints",
            environment=environment["communities"],
            layers=[
                pip_packages_layer,
                shared_layer,
            ],
        )

        # --------------------------------------------------------------------
        # Customers endpoints
        # --------------------------------------------------------------------
        CustomersStack(
            self, 
            f"{app_env.get_stage_name()}-{server_name}-customers-stack", 
            api=general_resource_v1, 
            app_environment=app_env,
            description="Stack for customers endpoints",
            environment=environment["customers"],
            layers=[
                pip_packages_layer,
                shared_layer,
            ],
        )

        # --------------------------------------------------------------------
        # Residents endpoints
        # TODO: Create a swagger for this endpoint
        # --------------------------------------------------------------------
        ResidentsStack(
            self, 
            f"{app_env.get_stage_name()}-{server_name}-residents-stack", 
            api=general_resource_v1, 
            app_environment=app_env,
            description="Stack for residents endpoints",
            environment=environment["residents"],
            layers=[
                pip_packages_layer,
                shared_layer,
                crypto_layer,
                mysql_layer,
            ],
        )

        # --------------------------------------------------------------------
        # Engrain Job and endpoints
        # --------------------------------------------------------------------
        EngrainStack(
            self, 
            f"{app_env.get_stage_name()}-{server_name}-engrain-stack",
            app_environment=app_env,
            description="Stack for Engrain Job",
            api=engrain_resource_v1,
            environment=environment["engrain"],
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
            f"{app_env.get_stage_name()}-{server_name}-tour-availability-stack",
            api=tour_resource_v2, 
            app_environment=app_env,
            description="Stack for Tour availability endpoints",
            environment=environment["touravailability"],
            layers=[
                pip_packages_layer,
                suds_layer,
                shared_layer
            ],
        )

        # --------------------------------------------------------------------
        # Conservice endpoints
        # TODO: Create a swagger for this endpoint
        # --------------------------------------------------------------------
        ConserviceStack(
            self, 
            f"{app_env.get_stage_name()}-{server_name}-conservice-stack", 
            api=general_resource_v2, 
            app_environment=app_env,
            description="Stack for conservice endpoints",
            environment=environment["conservice"],
            layers=[
                pip_packages_layer,
                shared_layer,
            ]
        )

        # --------------------------------------------------------------------
        # Salesforce endpoints
        # --------------------------------------------------------------------
        SalesforceStack(
            self,
            f"{app_env.get_stage_name()}-{server_name}-salesforce-stack",
            description="Stack for salesforce endpoints",
            api=salesforce_resource_v1,
            api_v2=salesforce_resource_v2,
            app_environment=app_env,
            environment=environment["salesforce"],
            layers=[
                salesforce_layer,
                shared_layer,
                pip_packages_layer,
            ],
        )
        
        # --------------------------------------------------------------------
        # Qoops for Jira automation endpoints
        # --------------------------------------------------------------------
        QoopsStack(
            self,
            f"{app_env.get_stage_name()}-{server_name}-jira-stack",
            description="Stack for submitting tickets to Quext's Jira system.",
            api=jira_resource_v2,
            app_environment=app_env,
            environment=environment["qoops"],
            layers=[
                jira_layer,
                shared_layer,
                pip_packages_layer,
            ],
        )

        # --------------------------------------------------------------------
        # One time link enpoint
        # TODO: Create a swagger for this endpoint
        # --------------------------------------------------------------------
        OneTimeLinkStack(
            self,
            f"{app_env.get_stage_name()}-{server_name}-onetime-link-stack",
            description="Stack for Onetime_link service",
            api=onetime_link_resource_v2,
            app_environment=app_env,
            environment=environment["onetimelink"],
            layers=[
                shared_layer,
                pip_packages_layer,
            ],
        )



        # --------------------------------------------------------------------
        # Rent dynamics enpoint
        # --------------------------------------------------------------------
        RentDynamicsStack(
            self,
            f"{app_env.get_stage_name()}-{server_name}-rent-dynamics-stack",
            description="Stack for Rent Dynamics service",
            api=rent_dynamics_resource_v2,
            app_environment=app_env,
            environment=environment["rentdynamics"],
            layers=[
                shared_layer,
                pip_packages_layer,
                mysql_layer
            ],
        )

        # --------------------------------------------------------------------
        # TruPay Google Job
        # --------------------------------------------------------------------
        TruePayGoogleStack(
            self, 
            f"{app_env.get_stage_name()}-{server_name}-trupay-google-stack",
            app_environment=app_env,
            description="Stack for TruPay Google Job",
            environment=environment["trupay-google"],
            layers=[
                mysql_layer,
                pip_packages_layer,
                shared_layer,
            ],
        )

