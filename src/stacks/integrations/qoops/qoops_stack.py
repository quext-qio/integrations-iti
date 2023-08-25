import os, boto3
from aws_cdk import (
    NestedStack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
    aws_sqs as sqs_,
    aws_iam as iam_,
    aws_lambda_event_sources as lambda_event_sources_,
    Aws,
)
from constructs import Construct
from src.utils.enums.app_environment import AppEnvironment

class QoopsStack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, api: apigateway_.RestApi, layers:list, environment: dict[str, str], app_environment: AppEnvironment, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # -----------------------------------------------------------------------
        # Constants
        timeout=Duration.seconds(900)
        allow_methods=['OPTIONS', 'POST']

        # --------------------------------------------------------------------
        # Create the QoopsQueue
        queue = sqs_.Queue(
            self, 
            f"{app_environment.get_stage_name()}-qoops-queue", 
            visibility_timeout=timeout,
            queue_name=f"{app_environment.get_stage_name()}-qoops-queue",
        )

        # --------------------------------------------------------------------
        # Create the API GW service role with permissions to call SQS
        # rest_api_role = iam_.Role(
        #     self,
        #     f"{app_environment.get_stage_name()}-rest-api-role",
        #     assumed_by=iam_.ServicePrincipal("apigateway.amazonaws.com"),
        #     managed_policies=[iam_.ManagedPolicy.from_aws_managed_policy_name("AmazonSQSFullAccess")]
        # )

        role_arn = os.getenv('ROLE_ARN', 'arn:aws:iam::273056594042:role/cdk-integrationApi-get-ssm-parameters')
        
        assumed_role = iam_.Role.from_role_arn(
            self,
            f"{app_environment.get_stage_name()}-assumed-role",
            role_arn=role_arn
        )

        # --------------------------------------------------------------------
        # Create API Integration Response object: 
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/IntegrationResponse.html
        integration_response = apigateway_.IntegrationResponse(
            status_code="200",
            response_templates={"application/json": ""},
        )

        # --------------------------------------------------------------------
        # Create API Integration Options object: 
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/IntegrationOptions.html
        api_integration_options = apigateway_.IntegrationOptions(
            credentials_role=assumed_role,
            integration_responses=[integration_response],
            request_templates={"application/json": "Action=SendMessage&MessageBody=$input.body"},
            passthrough_behavior=apigateway_.PassthroughBehavior.NEVER,
            request_parameters={"integration.request.header.Content-Type": "'application/x-www-form-urlencoded'"},
        )

        # --------------------------------------------------------------------
        # Create AWS Integration Object for SQS: 
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/AwsIntegration.html
        api_resource_sqs_integration = apigateway_.AwsIntegration(
            service="sqs",
            integration_http_method="POST",
            options=api_integration_options,
            path="{}/{}".format(Aws.ACCOUNT_ID, queue.queue_name),
        )

        # --------------------------------------------------------------------
        # Create a Method Response Object: 
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/MethodResponse.html
        method_response = apigateway_.MethodResponse(status_code="200")

        # --------------------------------------------------------------------
        # Add the API GW Integration to the API GW Resource
        api.add_method(
            "POST",
            api_resource_sqs_integration,
            method_responses=[method_response]
        )


        # --------------------------------------------------------------------
        # Creating Lambda function that will be triggered by the SQS Queue
        sqs_lambda = lambda_.Function(
            self, f"{app_environment.get_stage_name()}-jira-report-lambda-function",
            description=f"This lambda is used to report Jira issues using the {app_environment.get_stage_name()}-qoops-queue", 
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/qoops"),
            handler="lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-jira-report-lambda-function",
        )

        # --------------------------------------------------------------------
        # Create an SQS event source for Lambda
        sqs_event_source = lambda_event_sources_.SqsEventSource(queue)

        # Add SQS event source to the Lambda function
        sqs_lambda.add_event_source(sqs_event_source)





        # # --------------------------------------------------------------------
        # # Create lambda function instance for (# POST /jira/report)
        # post_lambda_function = lambda_.Function(
        #     self, 
        #     f"{app_environment.get_stage_name()}-jira-report-lambda-function",
        #     description=f"This lambda is used to report Jira issues using the {app_environment.get_stage_name()}-qoops-queue", 
        #     environment=environment,
        #     runtime=lambda_.Runtime.PYTHON_3_10,
        #     timeout=timeout,
        #     code=lambda_.Code.from_asset("./src/lambdas/qoops"),
        #     handler="lambda_function.lambda_handler",
        #     layers=layers,
        #     function_name=f"{app_environment.get_stage_name()}-jira-report-lambda-function",
        # )
        
    

        # # --------------------------------------------------------------------
        # # Resource to report issues (POST)
        # post_endpoint = api.add_resource(
        #     "report",
        #     default_cors_preflight_options=apigateway_.CorsOptions(
        #         allow_methods=allow_methods,
        #         allow_origins=apigateway_.Cors.ALL_ORIGINS
        #     ),    
        # )

        

        # # --------------------------------------------------------------------
        # # Create a Lambda integration instance
        # # POST
        # post_endpoint_lambda_integration = apigateway_.LambdaIntegration(
        #     post_lambda_function,
        #     proxy=True,
        #     integration_responses=[
        #         apigateway_.IntegrationResponse(
        #             status_code="200",
        #             response_templates={"application/json": ""},
        #             response_parameters={
        #                 'method.response.header.Access-Control-Allow-Origin': "'*'"
        #             }
        #         ),
        #     ],
        # )

        

        # # --------------------------------------------------------------------
        # # Add a POST method to endpoint
        # post_endpoint.add_method(
        #     'POST', 
        #     post_endpoint_lambda_integration,
        #     request_parameters={},
        #     method_responses=[
        #         apigateway_.MethodResponse(
        #             status_code="200",
        #             response_parameters={
        #                 'method.response.header.Access-Control-Allow-Origin': True
        #             }
        #         )
        #     ],
        # )

        

