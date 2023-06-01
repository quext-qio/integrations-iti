import aws_cdk as core
import aws_cdk.assertions as assertions

from integrations_iti.integrations_iti_stack import IntegrationsItiStack

# example tests. To run these tests, uncomment this file along with the example
# resource in integrations_iti/integrations_iti_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = IntegrationsItiStack(app, "integrations-iti")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
