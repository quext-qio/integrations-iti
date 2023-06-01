from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct
from stacks_definition.guestcards import GuestCard

class IntegrationsItiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # -----------------------------------------------------------------------
        # Guestcard 
        # TODO: load env from Parameter Store
        environment={
            "LOG_LEVEL": "INFO",
            "JIRA_REPORTER_TOKEN": "ATATT3xFfGF0jPYyx6LBni9zxGQByh3O7ojXxj2NS3YGosM5H0lEyWlvYl6XI-_j4luNaqfNORreXa1PpQg6gSp_LXuZ9jq8DQKAl4ZpX_QMFCwHrJhRvZuLejVGpSIYClhXeqBZ5M1f7RC851JBtYdcuwVrbtyJZLklNUfihHwudACRnbN8EIw=6416F982",
        }
        GuestCard.create_definition(
            stage_name="dev", 
            api_version="v1", 
            allow_methods=['OPTIONS', 'GET', 'POST'], 
            environment=environment
        )
        
        
