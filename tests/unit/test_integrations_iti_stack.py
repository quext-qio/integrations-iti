import aws_cdk as core
import aws_cdk.assertions as assertions
from src.stacks.guestcards_stack.guestcards_stack import GuestcardsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in integrations_iti/integrations_iti_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = GuestcardsStack(app, "GuestcardsStackTest")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
