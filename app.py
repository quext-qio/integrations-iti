#!/usr/bin/env python3
import os
import boto3
import aws_cdk as cdk
from src.stacks.integrations.guestcards_stack.guestcards_stack import GuestcardsStack
from src.stacks.integrations.units_stack.units_stack import UnitsStack
from src.stacks.integrations.communities_stack.communities_stack import CommunitiesStack
from src.stacks.integrations.transunion_stack.transunion_stack import TransUnionStack
from src.stacks.integrations.customers_stack.customers_stack import CustomersStack
from src.stacks.integrations.residents_stack.residents_stack import ResidentsStack
from src.stacks.integrations.engrain_stack.engrain_stack import EngrainStack
from src.stacks.integrations.tour_availability_stack.tour_availability_stack import TourAvailabilityStack
from src.stacks.integrations.conservice_stack.conservice_stack import ConserviceStack
from src.stacks.shared.api_stack.api_stack import APIStack
from src.stacks.shared.layers_stack.layers_stack import LayersStack
from src.stacks.shared.env_stack.env_stack import EnvStack
from src.utils.enums.stage_name import StageName
from src.stacks.root.root_stack import RootStack

# --------------------------------------------------------------------
# Create the app
app = cdk.App()


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
service_name = "integrationApi"
cdk.Tags.of(app).add(key="Project", value='quext', priority=300)
cdk.Tags.of(app).add(key="Team", value='integration', priority=300)
cdk.Tags.of(app).add(key="Environment", value=stage.value, priority=300)
cdk.Tags.of(app).add(key="Service", value=service_name, priority=300)

# --------------------------------------------------------------------
# Root stack
root_stack = RootStack(
    app, 
    f"{stage.value}-{server_name}-RootStack",
    stage=stage,
    main_app=app,
    server_name=server_name,
)

# --------------------------------------------------------------------
# Synth the app
app.synth()
# --------------------------------------------------------------------
