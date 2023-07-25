import os

from pydantic import BaseModel
from zato.server.service import Definition

from MessageBusShared.Controller.KafkaProducerGateway import KafkaProducerGateway
from MessageBusShared.Model.MessageModel import Header, Message
from VendorShared.Model.ServiceRequest import ServiceRequest


class MessageBusConstants:
    UNIT = 'unit'
    UNITSPACE = 'unitspace'
    PERSON = 'person'
    RESIDENT = 'residents'
    ADDRESS = 'address'
    LEASE = 'lease'
    LEASEINTERVAL = 'leaseinterval'
    SQLALCHEMY_OBJECT = "_sa_instance_state"


class MessageBusUtils:
    # Topic Names for posting the events
    generic_topic_name = os.getenv('GENERIC_KAFKA_MESSAGE_TOPIC')
    iot_topic_name = os.getenv('IOT_KAFKA_MESSAGE_TOPIC')


    def __init__(self):
        self.kafka_broker = KafkaProducerGateway()

    def send_event(self, service_request: ServiceRequest, header: Header, payload: dict,
                   topic: str = generic_topic_name) -> None:
        """
        Send Event to message bus

        @param service_request: ServiceRequest object
        @param header: Header Part of the event to post
        @param payload: Payload on the event to post
        @param topic: Topic Name of the Message Bus to send the event
        """
        self.kafka_broker.send_message(service_request.definition, topic, Message(header, payload))

    def send_iot_event(self, definition: Definition, payload: BaseModel, topic: str = iot_topic_name) -> None:
        """
        Send Event to message bus specifically to IOT

        @param definition: Definition object
        @param payload: Payload on the event to post
        @param topic: Topic Name of the Message Bus to send the event
        """
        self.kafka_broker.send_message(definition, topic, payload)
