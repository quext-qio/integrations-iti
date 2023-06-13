from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
)
from constructs import Construct

class UnitsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, api: apigateway_.RestApi , **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # -----------------------------------------------------------------------
        # Units 
        environment={
            "LOG_LEVEL": "INFO",
            "TEST": "test",
        }
        timeout=Duration.seconds(900)
        allow_methods=['OPTIONS', 'POST']
        
        # --------------------------------------------------------------------
        # Create Cerberus Layers

        cerberus_layer = lambda_.LayerVersion(
            self, "CerberusLayer",
            layer_version_name="CerberusLayer",
            description="Package documentation: https://docs.python-cerberus.org/en/stable/",
            code=lambda_.Code.from_asset("src/utils/layers/cerberus_layer.zip"),
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

        # --------------------------------------------------------------------
        # Create lambda function instance
        lambda_function = lambda_.Function(
            self, 
            "Units_Lambda_Function",
            description="Units Lambda is responsible for handling units per community",
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/units"),
            handler="lambda_function.lambda_handler",
            layers=[cerberus_layer],
            function_name="Units_Lambda_Function",
        )

        # -------------------------------------------------------------------- 
        # Add a resource to the base API and configure CORS options for the resource 
        general_units_endpoint = api.add_resource("general").add_resource(
            "units",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),    
        )

        # --------------------------------------------------------------------
        # Create a Lambda integration instance
        endpoint_lambda_integration = apigateway_.LambdaIntegration(
            lambda_function,
            proxy=True,
            integration_responses=[
                apigateway_.IntegrationResponse(
                    status_code="200",
                    response_templates={"application/json": ""},
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
            ],
        )

        # --------------------------------------------------------------------
        # Add a POST method to endpoint
        general_units_endpoint.add_method(
            'POST', 
            endpoint_lambda_integration,
            method_responses=[
                apigateway_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ],
        )
