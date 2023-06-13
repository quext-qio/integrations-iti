#!/usr/bin/env python3
import os
import aws_cdk as cdk
from src.stacks.guestcards_stack.guestcards_stack import GuestcardsStack
from src.stacks.units_stack.units_stack import UnitsStack
from src.stacks.placepay_stack.placepay_stack import PlacepayStack
from src.stacks.api_stack.api_stack import APIStack

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
# Stack for placepay endpoints
PlacepayStack(app, "PlacepayStack", api=api_v1)

# --------------------------------------------------------------------
# Stack for guestcards endpoints
GuestcardsStack(app, "GuestcardsStack", api=api_v1)

# --------------------------------------------------------------------
# Stack for units endpoints
UnitsStack(app, "UnitsStack", api=api_v2)

# --------------------------------------------------------------------
# Synth the app
app.synth()
# --------------------------------------------------------------------
