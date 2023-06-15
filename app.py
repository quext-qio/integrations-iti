#!/usr/bin/env python3
import os
import aws_cdk as cdk

from src.stacks.integrations.guestcards_stack.guestcards_stack import GuestcardsStack
from src.stacks.integrations.units_stack.units_stack import UnitsStack
from src.stacks.integrations.placepay_stack.placepay_stack import PlacepayStack
from src.stacks.integrations.communities_stack.communities_stack import CommunitiesStack
from src.stacks.integrations.transunion_stack.transunion_stack import TransUnionStack
from src.stacks.integrations.customers_stack.customers_stack import CustomersStack
from src.stacks.shared.api_stack.api_stack import APIStack
from src.stacks.shared.layers_stack.layers_stack import LayersStack

# --------------------------------------------------------------------
# Create the app
app = cdk.App()

# --------------------------------------------------------------------
# API Gateway for share with all lambda's functions
api_stack = APIStack(
    app, 
    "APIStack", 
    stage_name="dev"
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

# --------------------------------------------------------------------
# Suported third party services v2
placepay_resource_v2 = api_v2.add_resource("placepay")
resman_resource_v2 = api_v2.add_resource("resman")
general_resource_v2 = api_v2.add_resource("general")
transunion_resource_v2 = api_v2.add_resource("transunion")

# --------------------------------------------------------------------
# Load all layers to share between lambda's functions
layer_stack =  LayersStack(app, "LayersStack")
cerberus_layer = layer_stack.get_cerberus_layer
place_api_layer = layer_stack.get_place_api_layer
requests_layer = layer_stack.get_requests_layer

# --------------------------------------------------------------------
# Stack for placepay endpoints
PlacepayStack(
    app, 
    "PlacepayStack", 
    api=placepay_resource_v1, 
    layers=[cerberus_layer, place_api_layer],
)

# --------------------------------------------------------------------
# Stack for guestcards endpoints
GuestcardsStack(
    app, 
    "GuestcardsStack", 
    api=resman_resource_v1,
    layers=[cerberus_layer],
)

# --------------------------------------------------------------------
# Stack for transunion endpoints
TransUnionStack(
    app, 
    "TransUnionStack", 
    api=transunion_resource_v1, 
    layers=[cerberus_layer, requests_layer],
)

# --------------------------------------------------------------------
# Stack for units endpoints
UnitsStack(
    app, 
    "UnitsStack", 
    api=general_resource_v2, 
    layers=[cerberus_layer],
)

# --------------------------------------------------------------------
# Stack for communities endpoints
CommunitiesStack(
    app, 
    "CommunitiesStack", 
    api=general_resource_v1, 
    layers=[cerberus_layer, requests_layer],
)

# --------------------------------------------------------------------
# Stack for customers endpoints
CustomersStack(
    app, 
    "CustomersStack", 
    api=general_resource_v1, 
    layers=[cerberus_layer, requests_layer],
)
# --------------------------------------------------------------------
# Synth the app
app.synth()
# --------------------------------------------------------------------
