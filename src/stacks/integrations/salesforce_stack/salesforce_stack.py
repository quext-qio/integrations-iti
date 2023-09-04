from aws_cdk import (
    NestedStack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
)
from constructs import Construct
from src.utils.enums.app_environment import AppEnvironment

class SalesforceStack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, api: apigateway_.RestApi, api_v2: apigateway_.RestApi, layers:list, environment: dict[str, str], app_environment: AppEnvironment, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # -----------------------------------------------------------------------
        # Constants
        timeout=Duration.seconds(900)
        allow_methods=['OPTIONS', 'GET']
        
        # --------------------------------------------------------------------
        # Version #1
        # --------------------------------------------------------------------
        # Create lambda function instance for (# GET api/v1/salesforce/liftoff)
        lambda_function = lambda_.Function(
            self, 
            f"{app_environment.get_stage_name()}-salesforce-v1-liftoff-lambda-function",
            description="Salesforce Lambda is responsible retrieving data from Salesforce using simple_salesforce library.", 
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_8,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/salesforce"),
            handler="lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-salesforce-dynamic-lambda-function",
        )
        

        # --------------------------------------------------------------------
        # Resource to execute query (GET)
        get_endpoint = api.add_resource(
            "liftoff",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),  
        )
        

        # --------------------------------------------------------------------
        # Create a Lambda integration instance
        # GET
        get_endpoint_lambda_integration = apigateway_.LambdaIntegration(
            lambda_function,
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

        # --------------------------------------------------------------------
        # Add a GET method to endpoint
        get_endpoint.add_method(
            'GET', 
            get_endpoint_lambda_integration,
            request_parameters={},
            method_responses=[
                apigateway_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                ),
            ],
            #api_key_required=True,
        )

        # --------------------------------------------------------------------
        # Version #2
        # --------------------------------------------------------------------
        # Create lambda function instance for (# GET api/v2/salesforce/liftoff)
        lambda_function_v2 = lambda_.Function(
            self, 
            f"{app_environment.get_stage_name()}-salesforce-v2-liftoff-lambda-function",
            description="Salesforce V2 Lambda is responsible retrieving data from Salesforce using simple_salesforce library.", 
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_8,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/v2/salesforce"),
            handler="lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-salesforce-v2-liftoff-lambda-function",
        )
        

        # --------------------------------------------------------------------
        # Resource to execute query (GET)
        get_endpoint_v2 = apiv2.add_resource(
            "liftoff",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),  
        )
        

        # --------------------------------------------------------------------
        # Create a Lambda integration instance
        # GET
        get_endpoint_lambda_integration_v2 = apigateway_.LambdaIntegration(
            lambda_function_v2,
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

        # --------------------------------------------------------------------
        # Add a GET method to endpoint
        get_endpoint_v2.add_method(
            'GET', 
            get_endpoint_lambda_integration_v2,
            request_parameters={},
            method_responses=[
                apigateway_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                ),
            ],
        )