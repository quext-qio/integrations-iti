from aws_cdk import (
    NestedStack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
)
from constructs import Construct

class SalesforceStack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, api: apigateway_.RestApi, layers:list, environment: dict[str, str], **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # -----------------------------------------------------------------------
        # Constants
        timeout=Duration.seconds(900)
        allow_methods=['OPTIONS', 'POST']
        
        # --------------------------------------------------------------------
        # Create lambda function instance for (# POST /salesforce/query)
        post_lambda_function = lambda_.Function(
            self, 
            "Salesforce_Dynamic_Lambda_Function",
            description="Salesforce Lambda is responsible retrieving data from Salesforce using simple_salesforce library.", 
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_8,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/salesforce"),
            handler="lambda_function.lambda_handler",
            layers=layers,
            function_name="Salesforce_Dynamic_Lambda_Function",
        )

        # --------------------------------------------------------------------
        # Resource to execute query (POST)
        post_endpoint = api.add_resource(
            "query",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),    
        )

        # --------------------------------------------------------------------
        # Define a model for the expected request body
        request_model = api.add_model(
            "RequestModel",
            content_type="application/json",
            schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "minLength": 1}
                },
                "required": ["query"]
            }
        )

        # --------------------------------------------------------------------
        # Create a Lambda integration instance
        # POST
        post_endpoint_lambda_integration = apigateway_.LambdaIntegration(
            post_lambda_function,
            proxy=True,
            request_templates={"application/json": request_model.to_json_template()},
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
        # Add a POST method to endpoint
        post_endpoint.add_method(
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

