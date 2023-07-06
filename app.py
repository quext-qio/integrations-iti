#!/usr/bin/env python3
import os
import aws_cdk as cdk
from src.stacks.integrations.guestcards_stack.guestcards_stack import GuestcardsStack
from src.stacks.integrations.units_stack.units_stack import UnitsStack
from src.stacks.integrations.placepay_stack.placepay_stack import PlacepayStack
from src.stacks.integrations.communities_stack.communities_stack import CommunitiesStack
from src.stacks.integrations.transunion_stack.transunion_stack import TransUnionStack
from src.stacks.integrations.customers_stack.customers_stack import CustomersStack
from src.stacks.integrations.residents_stack.residents_stack import ResidentsStack
from src.stacks.integrations.engrain_stack.engrain_stack import EngrainStack
from src.stacks.integrations.tour_availability_stack.tour_availability_stack import TourAvailabilityStack
from src.stacks.shared.api_stack.api_stack import APIStack
from src.stacks.shared.layers_stack.layers_stack import LayersStack
from src.stacks.shared.env_stack.env_stack import EnvStack
from src.utils.enums.stage_name import StageName

# --------------------------------------------------------------------
# Create the app
app = cdk.App()

# --------------------------------------------------------------------
# Setting the environment variable PACKAGES to True will 
# re-create the package for [pip_packages_layer]
#
# Setting the environment variable PACKAGES to False will
# use the package already created in [src/utils/layers/pip_packages_layer.zip]
should_create_dynamic_packages = os.getenv('PACKAGES', False)

# --------------------------------------------------------------------
# Stage to deploy
current_stage = os.getenv('STAGE', 'dev')
if current_stage == 'stage':
    stage = StageName.STAGE
elif current_stage == 'prod':
    stage = StageName.PROD
else:
    stage = StageName.DEV
print(f"Stage seleted: {stage.value}")

# --------------------------------------------------------------------
# Tags for all resources
server_name = "aws-integration-engine"
tags = {
    'Environment': stage.value,
    'Project': 'quext',
    'Service': server_name,
    'Team': 'integration'
}

# --------------------------------------------------------------------
# Role for quext-shared-services
role_arn = os.getenv('ROLE_ARN', 'arn:aws:iam::273056594042:role/cdk-integrationApi-get-ssm-parameters')


# --------------------------------------------------------------------
# Environment variables for share with all lambda's functions
env_stack = EnvStack(
    app, 
    f"{stage.value}-{server_name}-envStack", 
    stage_name=stage,
    description="Stack load environment variables for all lambda's functions",
    tags=tags,
    role_arn=role_arn,
)
environment=env_stack.get_env

# --------------------------------------------------------------------
# API Gateway for share with all lambda's functions
api_stack = APIStack(
    app, 
    f"{stage.value}-{server_name}-apiStack", 
    stage_name=stage,
    description="Stack load API Gateway for all lambda's functions",
    tags=tags,
)
api=api_stack.get_api

# --------------------------------------------------------------------
# Current supported versions
api_v1 = api.add_resource("v1")
api_v2 = api.add_resource("v2")

# --------------------------------------------------------------------
# Suported third party services v1
placepay_resource_v1 = api_v1.add_resource("placepay")
resman_resource_v1 = api_v1.add_resource("resman")
general_resource_v1 = api_v1.add_resource("general")
transunion_resource_v1 = api_v1.add_resource("transunion")
tour_resource_v1 = api_v1.add_resource("tour")

# --------------------------------------------------------------------
# Suported third party services v2
placepay_resource_v2 = api_v2.add_resource("placepay")
resman_resource_v2 = api_v2.add_resource("resman")
general_resource_v2 = api_v2.add_resource("general")
transunion_resource_v2 = api_v2.add_resource("transunion")
tour_resource_v2 = api_v2.add_resource("tour")

# --------------------------------------------------------------------
# Load all layers to share between lambda's functions
layer_stack =  LayersStack(
    app, 
    f"{stage.value}-{server_name}-layersStack",
    description="Stack load all layers to share between lambda's functions",
    tags=tags, 
    should_create_dynamic_packages=should_create_dynamic_packages,   
)
place_api_layer = layer_stack.get_place_api_layer
mysql_layer = layer_stack.get_mysql_layer
zeep_layer = layer_stack.get_zeep_layer
suds_layer = layer_stack.get_suds_layer
shared_layer = layer_stack.get_shared_layer
pip_packages_layer = layer_stack.get_pip_packages_layer
crypto_layer = layer_stack.get_crypto_layer

# --------------------------------------------------------------------
# Stack for placepay endpoints
PlacepayStack(
    app, 
    f"{stage.value}-{server_name}-placepayStack", 
    api=placepay_resource_v1, 
    environment=environment,
    description="Stack for placepay endpoints",
    tags=tags,
    layers=[
        place_api_layer,
        shared_layer,
        pip_packages_layer,
    ],
)

# --------------------------------------------------------------------
# Stack for guestcards endpoints
GuestcardsStack(
    app, 
    f"{stage.value}-{server_name}-guestcardsStack", 
    api=resman_resource_v1,
    description="Stack for guestcards endpoints",
    tags=tags,
    layers=[
        pip_packages_layer,
        shared_layer,
    ],
)

# --------------------------------------------------------------------
# Stack for transunion endpoints
TransUnionStack(
    app, 
    f"{stage.value}-{server_name}-transUnionStack", 
    api=transunion_resource_v1, 
    environment=environment,
    description="Stack for transunion endpoints",
    tags=tags,
    layers=[
        pip_packages_layer,
        shared_layer,
    ],
)

# --------------------------------------------------------------------
# Stack for units endpoints
UnitsStack(
    app, 
    f"{stage.value}-{server_name}-unitsStack", 
    api=general_resource_v2, 
    environment=environment,
    description="Stack for units endpoints",
    tags=tags,
    layers=[
        pip_packages_layer, 
        mysql_layer, 
        zeep_layer, 
        suds_layer, 
        shared_layer,
    ],
)

# --------------------------------------------------------------------
# Stack for communities endpoints
CommunitiesStack(
    app, 
    f"{stage.value}-{server_name}-communitiesStack", 
    api=general_resource_v1, 
    description="Stack for communities endpoints",
    tags=tags,
    layers=[
        pip_packages_layer,
        shared_layer,
    ],
    environment=environment,
)

# --------------------------------------------------------------------
# Stack for customers endpoints
CustomersStack(
    app, 
    f"{stage.value}-{server_name}-customersStack", 
    api=general_resource_v1, 
    description="Stack for customers endpoints",
    tags=tags,
    layers=[
        pip_packages_layer,
        shared_layer,
    ],
    environment=environment,
)

# --------------------------------------------------------------------
# Stack for customers endpoints
ResidentsStack(
    app, 
    f"{stage.value}-{server_name}-residentsStack", 
    api=general_resource_v1, 
    description="Stack for residents endpoints",
    tags=tags,
    layers=[
        pip_packages_layer,
        shared_layer,
        crypto_layer,
        mysql_layer,
    ],
    environment=environment,
)

# --------------------------------------------------------------------
# Stack for Engrain Job
EngrainStack(
    app, 
    f"{stage.value}-{server_name}-engrainStack",
    environment=environment,
    description="Stack for Engrain Job",
    tags=tags,
    layers=[
        pip_packages_layer,
        shared_layer,
    ],
)
# --------------------------------------------------------------------
# Stack for Tours endpoints
TourAvailabilityStack(
    app, 
    f"{stage.value}-{server_name}-tourAvailabilityStack",
    api=tour_resource_v2, 
    layers=[
        pip_packages_layer,
        suds_layer,
        shared_layer
    ],
    environment=environment,
    description="Stack for Tour availability endpoints",
    tags=tags,
)


# --------------------------------------------------------------------
# Synth the app
app.synth()
# --------------------------------------------------------------------
