#!/usr/bin/env python3
import os

import aws_cdk as cdk

from integrations_iti.integrations_iti_stack import IntegrationsItiStack
from units_stack.units_stack import UnitsStack

app = cdk.App()
IntegrationsItiStack(app, "IntegrationsItiStack")
UnitsStack(app, "UnitsStack")

app.synth()
