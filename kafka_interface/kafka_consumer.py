"""
Defines a websocket consumer for handling incoming connections
"""
import json
import threading

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from kafka import KafkaConsumer

KAFKA_CONSUMER_TOPIC = 'detection'
KAFKA_SERVER_IP = '10.12.42.157:9092'
KAFKA_GROUP_ID = 'camera_events'


class AppKafkaConsumer:
    """
    Handles consuming kafka msgs and sending them to the channel layer of
    django
    """

    def __init__(self):
        print("Initializing Kafka Consumer...")
        self.detection_consumer = KafkaConsumer(
            KAFKA_CONSUMER_TOPIC,
            bootstrap_servers=[KAFKA_SERVER_IP],
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id=KAFKA_GROUP_ID,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')))

        self.detection_consumer.poll()
        self.detection_consumer.seek_to_end()

    def init_thread(self):
        threading.Thread(
            target=self.consume_and_send_to_channel).start()

    def consume_and_send_to_channel(self):
        """
        Gets kafka msgs and sends them to kafka group of django
        """
        try:
            for detection in self.detection_consumer:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    KAFKA_GROUP_ID,
                    {
                        'type': 'kafka_msg_update',
                        'message': detection.value
                    }
                )

        except Exception as exc:
            print("Exception raised in kafka consumer: {}".format(exc))
