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
        #allow_methods=['OPTIONS', 'POST']

        # --------------------------------------------------------------------
        # Create the QoopsQueue
        queue = sqs_.Queue(
            self, 
            f"{app_environment.get_stage_name()}-qoops-queue", 
            visibility_timeout=timeout,
            queue_name=f"{app_environment.get_stage_name()}-qoops-queue",
        )

        # --------------------------------------------------------------------
        # # Load session using default AWS credentials
        # aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID')
        # aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        # aws_session_token=os.getenv('AWS_SESSION_TOKEN')

        # session = boto3.Session(
        #     aws_access_key_id=aws_access_key_id,
        #     aws_secret_access_key=aws_secret_access_key,
        #     aws_session_token=aws_session_token,
        # )

        # Create a client to interact with the STS (Security Token Service)
        #sts_client = session.client("sts")

        #role_arn = os.getenv('ROLE_ARN', 'arn:aws:iam::273056594042:role/cdk-integrationApi-get-ssm-parameters')
        
        #aws_role_arn=os.getenv("AWS_ROLE")


        # Assume the IAM role
        # assume_role = sts_client.assume_role(
        #     RoleArn=role_arn,
        #     RoleSessionName=f"{app_environment.get_stage_name()}-sqs-assumed-session"
        # )

        # # Extract the temporary credentials from the assume_role
        # credentials = assume_role['Credentials']

        # # Create a new session using the temporary credentials
        # new_session = boto3.Session(
        #     aws_access_key_id=credentials['AccessKeyId'],
        #     aws_secret_access_key=credentials['SecretAccessKey'],
        #     aws_session_token=credentials['SessionToken'],
        # )

        # # Create a client to interact with SQS (Simple Queue Service)
        # sqs_client = new_session.client(
        #     "sqs",
        #     region_name="us-east-1",
        # )

        
    

        # Create the API GW service role with permissions to call SQS
        rest_api_role = iam_.Role(
            self,
            f"{app_environment.get_stage_name()}-qoops-api-role",
            role_name=f"{app_environment.get_stage_name()}-rest-api-role",
            description="Qoops Role for API Gateway to call SQS",
            assumed_by=iam_.ServicePrincipal("apigateway.amazonaws.com"),
            managed_policies=[iam_.ManagedPolicy.from_aws_managed_policy_name("AmazonSQSFullAccess")]
        )
        #print(type(rest_api_role))

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
            credentials_role=rest_api_role,
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
