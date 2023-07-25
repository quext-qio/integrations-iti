import json
import logging
from json import JSONDecoder

from pykafka.common import OffsetType
from zato.server.service import Definition

from MessageBusShared.Model.MessageModel import Message


class KafkaConsumerGateway:
    """Kafka Message Consumer Service plays a vital role in reading the message from message bus"""

    _broker_channel_name = 'KafkaBroker'
    _consumer_group_name = 'zato-consumer-group'

    def read_message(self, definition: Definition, topic: str):
        """
        Reading messages from kafka message bus

        Parameters:
        ----------
        @param service_request: ServiceRequest object holds kafka connection definition
        @param topic: Topic Name to which the message needs to read
        """

        # Getting Broker Connection Client
        logging.info("Broker to connect : %s", self._broker_channel_name)
        connection = definition.kafka[self._broker_channel_name].conn
        client_conn = connection.client

        # Selecting the topic for the producer
        logging.info("Topic name to use: %s", topic)
        topic = client_conn.topics[topic]

        # If kafka connection uses zookeeper then we go for balanced_consumer
        # else we go for simple_consumer
        consumer = topic.get_balanced_consumer(
            consumer_group=self._consumer_group_name) if connection.config.should_use_zookeeper \
            else topic.get_simple_consumer(
            consumer_group=self._consumer_group_name,
            auto_offset_reset=OffsetType.EARLIEST,
            reset_offset_on_start=True
        )

        for message in consumer:
            # Skipping null messages and SYNC-SERVICE source messages
            if message is not None:
                value = message.value
                parsed_message = json.loads(value, cls=JSONDecoder)
                logging.info("Message : %s", parsed_message)
                message_obj = Message(**parsed_message)
                logging.info("Obj : %s", message_obj)
                if message_obj.header["source"] != 'SYNC_SERVICE':
                    logging.info("Message Id : %s", message_obj.header["message_id"])
