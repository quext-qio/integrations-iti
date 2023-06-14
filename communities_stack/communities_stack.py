from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
)
from constructs import Construct

class CommunitiesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # -----------------------------------------------------------------------
        # Constants
        environment={
            "LOG_LEVEL": "INFO",
           # "PLACE_PAY_API_KEY": "test_private_key__-yK6oFDnaJFwIrhVcCfI5r",
        }
        stage_name="dev"
        timeout=Duration.seconds(900)
        allow_methods=['OPTIONS', 'POST']
        
        # --------------------------------------------------------------------
        # Create Cerberus Layers
        cerberus_layer = lambda_.LayerVersion(
            self, "CerberusLayer",
            layer_version_name="CerberusLayer",
            description="Package documentation: https://docs.python-cerberus.org/en/stable/",
            code=lambda_.Code.from_asset("./utils/layers/cerberus_layer.zip"),
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
        # Create lambda function instance for (# POST /placepay/new-account)
        lambda_function = lambda_.Function(
            self, 
            "Auth_Get_Communities",
            description="This Lambda is responsible to get a communities list according to a specific customerUUID", 
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./lambdas/communities"),
            handler="lambda_function.lambda_handler",
            layers=[cerberus_layer],
            function_name="Auth_Get_Communities",
        )
        
        # --------------------------------------------------------------------
        # Create a Rest API instance
        base_api = apigateway_.RestApi(
            self, "Integrations_Api", 
            rest_api_name="Integrations_Api", 
            description="Base API Gateway for Zato to AWS Migration",
            deploy_options=apigateway_.StageOptions(
                stage_name=stage_name, 
                logging_level=apigateway_.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
            ),
            endpoint_configuration=apigateway_.EndpointConfiguration(
                types=[apigateway_.EndpointType.REGIONAL]
            ),
        )

        # -------------------------------------------------------------------- 
        # Add a resource to the base API and configure CORS options for the resource 
        # api = /api/v1/general/communities
        api = base_api.root.add_resource("api").add_resource("v1").add_resource("general").add_resource("communities",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),    
        )

        # --------------------------------------------------------------------
        # Create a Lambda integration instance
        # POST
        post_endpoint_lambda_integration = apigateway_.LambdaIntegration(
            lambda_function,
            proxy=False,
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
        api.add_method(
            'POST', 
            post_endpoint_lambda_integration,
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
