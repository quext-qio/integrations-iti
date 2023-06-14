#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import aws_cdk as cdk

from integrations_iti.integrations_iti_stack import IntegrationsItiStack
from units_stack.units_stack import UnitsStack
from placepay_stack.placepay_stack import PlacepayStack
from communities_stack.communities_stack import CommunitiesStack

load_dotenv()


app = cdk.App()
IntegrationsItiStack(app, "IntegrationsItiStack")
UnitsStack(app, "UnitsStack")
PlacepayStack(app, "PlacepayStack")
CommunitiesStack(app, "CommunitiesStack")

app.synth()
