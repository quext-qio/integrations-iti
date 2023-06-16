from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
    aws_ssm as ssm
)
from constructs import Construct


class TransUnionStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, api: apigateway_.RestApi, layers:list, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Constants
        environment={
          "parameter_store": ssm.StringParameter.from_string_parameter_attributes(self, "parameter_store", parameter_name="/integrations/aws/migration").string_value
        }
        timeout=Duration.seconds(900)
        allow_methods=["OPTIONS", "POST"]

        # ------------- handles the identity lambda ------------- #
        # Creates lambda function instance for (# POST /transunion/identity)
        identity_lambda_function = lambda_.Function(
            self, 
            "TransUnion_Identity_Lambda_Function",
            description="Handles the verification and evaluation processes with TransUnion", 
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/transunion"),
            handler="identity_lambda_function.lambda_handler",
            layers=layers,
            function_name="TransUnion_Identity_Lambda_Function",
        )

        # Identity
        identity_endpoint = api.add_resource(
            "identity",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),    
        )

        # Create a Lambda integration instance
        # Identity
        identity_endpoint_lambda_integration = apigateway_.LambdaIntegration(
            identity_lambda_function,
            proxy=True,
            integration_responses=[
                apigateway_.IntegrationResponse(
                    status_code="200",
                    response_templates={"application/json": ""},
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin":"'*'"
                    }
                ),
            ],
        )

        # Add a POST method to endpoint
        identity_endpoint.add_method(
            "POST", 
            identity_endpoint_lambda_integration,
            request_parameters={},
            method_responses=[
                apigateway_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True
                    }
                )
            ],
        )

        # ------------- handles the resident screening lambda ------------- #
        # Creates lambda function instance for (# POST /transunion/screening)
        screening_lambda_function = lambda_.Function(
            self, 
            "TransUnion_Screening_Lambda_Function",
            description="Handles the resident screening processes with TransUnion", 
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/transunion"),
            handler="screening_lambda_function.lambda_handler",
            layers=layers,
            function_name="TransUnion_Screening_Lambda_Function",
        )

        # Resident screening
        screening_endpoint = api.add_resource(
            "screening",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),    
        )

        # Create a Lambda integration instance
        screening_endpoint_lambda_integration = apigateway_.LambdaIntegration(
            screening_lambda_function,
            proxy=True,
            integration_responses=[
                apigateway_.IntegrationResponse(
                    status_code="200",
                    response_templates={"application/json": ""},
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin":"'*'"
                    }
                ),
            ],
        )

        # Add a POST method to endpoint
        screening_endpoint.add_method(
            "POST", 
            screening_endpoint_lambda_integration,
            request_parameters={},
            method_responses=[
                apigateway_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True
                    }
                )
            ],
        )

