from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
    aws_ssm as ssm
)
from constructs import Construct


class TransUnionStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, api: apigateway_.RestApi , **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Constants
        environment={
          'trans_union_postback_url': ssm.StringParameter.from_string_parameter_attributes(self, 'TRANS_UNION_POST_BACK_URL', parameter_name='/integrations/aws/migration').string_value
        }

        timeout=Duration.seconds(900)
        allow_methods=['OPTIONS', 'POST']
        
        # Create Cerberus Layers
        cerberus_layer = lambda_.LayerVersion(
            self, "CerberusLayer",
            layer_version_name="CerberusLayer",
            description="Package documentation: https://docs.python-cerberus.org/en/stable/",
            code=lambda_.Code.from_asset("./src/utils/layers/cerberus_layer.zip"),
            compatible_runtimes=[
                lambda_.Runtime.PYTHON_3_10, 
                lambda_.Runtime.PYTHON_3_9, 
                lambda_.Runtime.PYTHON_3_8, 
                lambda_.Runtime.PYTHON_3_7, 
                lambda_.Runtime.PYTHON_3_6,
            ],
            compatible_architectures=[
                lambda_.Architecture.ARM_64, 
                lambda_.Architecture.X86_64,
            ],
        )

        # Creates lambda function instance for (# POST /transunion/rental)
        rental_lambda_function = lambda_.Function(
            self, 
            "TransUnion_Rental_Lambda_Function",
            description="Handles the verification and evaluation processes with TransUnion", 
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/transunion"),
            handler="rental_lambda_function.lambda_handler",
            layers=[cerberus_layer],
            function_name="TransUnion_Rental_Lambda_Function",
        )

        # Add base resource to API Gateway
        api = api.add_resource("transunion")

        # Rental
        rental_endpoint = api.add_resource(
            "rental",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),    
        )

        # Create a Lambda integration instance
        # Rental
        rental_endpoint_lambda_integration = apigateway_.LambdaIntegration(
            rental_lambda_function,
            proxy=True,
            integration_responses=[
                apigateway_.IntegrationResponse(
                    status_code="200",
                    response_templates={"application/json": ""},
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                ),
            ],
        )

        # Add a POST method to endpoint
        rental_endpoint.add_method(
            'POST', 
            rental_endpoint_lambda_integration,
            request_parameters={},
            method_responses=[
                apigateway_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ],
        )

