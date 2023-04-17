import json
import logging
from datetime import datetime
import os
from pykafka.exceptions import SocketDisconnectedError, LeaderNotAvailable
from pykafka.partitioners import HashingPartitioner
from zato.server.service import Definition
from MessageBusShared.Model.MessageModel import Message, MessageEncoder
from pykafka.partitioners import hashing_partitioner


class KafkaProducerGateway:
    """Kafka Message Producer Service plays a vital role in posting the message to message bus"""

    _broker_channel_name = 'KafkaBroker'

    def send_message(self, definition: Definition, topic: str, message: Message):
        """
        Sending message to kafka message bus for other services to get consume it
        Parameters:
        ----------
        @param definition: Definition object holds kafka connection definition
        @param topic: Topic Name to which the message needs to send
        @param message: Message to post to kafka message bus
        """
        kafka_status = True
        current_time = datetime.strftime(datetime.today(),'%Y-%m-%dT%H:%M:%S.%f')
        try:
            kafka_status = definition.kafka[self._broker_channel_name].is_active
        except Exception as error:
            logging.info("error: %s" %error)
            kafka_status = False
        finally:
            if not kafka_status:
                logging.info("Kafka Server turned off in Zato Webadmin.") # is_active = False
                return

        logging.debug("input_data : %s", json.dumps(message.dict(), indent=4, cls=MessageEncoder))
        input_data = bytes(json.dumps(message.dict(), indent=4, cls=MessageEncoder), "ascii")

        #  Getting Broker Connection Client
        logging.info("Broker to connect : %s", self._broker_channel_name)
        client_conn = definition.kafka[self._broker_channel_name].conn.client

        #  Selecting the topic for the producer
        logging.info("Topic name to use: %s", topic)
        topic = client_conn.topics[topic]

        #  Getting the Producer Object to send messages to kafka message bus
        with topic.get_producer(linger_ms=0,sync=False,partitioner=hashing_partitioner) as producer:
            try:
                logging.info("Sending message to broker - topic name : {}".format(topic))
                if topic == os.getenv('GENERIC_KAFKA_MESSAGE_TOPIC'):
                    producer.produce(message=input_data, partition_key=message.header.partition_key,
                                 timestamp=message.header.timestamp)
                elif topic == os.getenv('IOT_KAFKA_MESSAGE_TOPIC'):
                    producer.produce(message=input_data, timestamp=current_time)
                logging.info("Message sent to broker is successful")
            except (SocketDisconnectedError, LeaderNotAvailable) as e:
                logging.error(e)
                self.__reconnect_producer(topic=topic, message=message, partitioner=hashing_partitioner, current_time=current_time)

    @staticmethod
    def __reconnect_producer(topic, message: Message, partitioner:HashingPartitioner, current_time):
        input_data = bytes(json.dumps(message.dict(), indent=4, cls=MessageEncoder), "ascii")
        producer = topic.get_sync_producer(partitioner=partitioner)
        logging.info("Reconnecting to producer")
        producer.stop()
        producer.start()
        logging.info("Sending message to broker")

        if topic == os.getenv('GENERIC_KAFKA_MESSAGE_TOPIC'):
            producer.produce(message=input_data, partition_key=message.header.partition_key,
                            timestamp=message.header.timestamp)
        elif topic == os.getenv('IOT_KAFKA_MESSAGE_TOPIC'):
            producer.produce(message=input_data, timestamp=current_time)
        logging.info("Message sent to broker is successful")
