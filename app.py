#!/usr/bin/env python3
import aws_cdk as cdk
from src.utils.enums.app_environment import AppEnvironment
from src.stacks.root.root_stack import RootStack

# --------------------------------------------------------------------
# Create the app
app = cdk.App()

# --------------------------------------------------------------------
# Stage to deploy
stage = AppEnvironment.get_current_stage()
print(f"Stage seleted: {stage.get_stage_name()}")

# --------------------------------------------------------------------
# Tags for all resources
server_name = "aws-integration-engine"
service_name = "integrationApi"
cdk.Tags.of(app).add(key="project", value='quext', priority=300)
cdk.Tags.of(app).add(key="team", value='integration', priority=300)
cdk.Tags.of(app).add(key="environment", value=stage.get_stage_name(), priority=300)
cdk.Tags.of(app).add(key="service", value=service_name, priority=300)

# --------------------------------------------------------------------
# Env configuration
env_config = cdk.Environment(
    account=stage.get_account_id(),
    region=stage.get_region(),
)

# --------------------------------------------------------------------
# Root stack
root_stack = RootStack(
    app, 
    f"{stage.get_stage_name()}-{server_name}-root-stack",
    app_env=stage,
    server_name=server_name,
    env=env_config,
)

# --------------------------------------------------------------------
# Synth the app
app.synth()
# --------------------------------------------------------------------
