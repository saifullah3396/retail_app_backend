"""
Defines a websocket consumer for handling incoming connections
"""
import asyncio
import json
import threading

import matplotlib.pyplot as plt
import numpy as np
from aiokafka import AIOKafkaConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from heat_maps.models import DensityHistogram
from kafka import KafkaConsumer, TopicPartition
from matplotlib.image import NonUniformImage
from scipy.ndimage.filters import gaussian_filter

KAFKA_SERVER_IP = '10.12.42.157:9092'

DS_SERVERS = [
    {
        "topic": "camera_events1",
        "group_id": "1"
    },
    {
        "topic": "camera_events2",
        "group_id": "1"
    },
    # {
    #     "topic": "camera_events3",
    #     "group_id": "1"
    # },
    # {
    #     "topic": "camera_events4",
    #     "group_id": "1"
    # },
    # {
    #     "topic": "camera_events5",
    #     "group_id": "1"
    # },
    {
        "topic": "camera_events2",
        "group_id": "2"
    }
]


class KafkaMessageProcessor:
    """
    Processes kafka messages as required
    """

    def __init__(self, topic):
        self.topic = topic

    def __call__(self, msg):
        raise NotImplementedError()


class DjangoChannelsInterface(KafkaMessageProcessor):
    """
    Processes kafka messages and sends them to django channels group
    """

    def __init__(self, topic):
        super().__init__(topic)

    def __call__(self, msg):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            self.topic,
            {
                'type': 'kafka_msg_update',
                'message': msg.value
            }
        )


class HeatMapGenerator(KafkaMessageProcessor):
    """
    Processes kafka messages to generate heat maps
    """

    def __init__(self, topic, data_process_size=200):
        super().__init__(topic)
        self.num_bins = 100
        self.range_x = (0, 44.577)
        self.range_y = (44.577, 35.2806)
        self.data_points_x = []
        self.data_points_y = []
        self.data_process_size = data_process_size
        self.xedges, self.yedges = \
            np.linspace(*range_x, self.num_bins), \
            np.linspace(*range_y, self.num_bins)
        self.hist2d = None

    def __call__(self, msg):
        if 'objects' in msg:
            for obj in msg['objects']:
                self.data_points_x.append(
                    obj['coordinates']['x'])
                self.data_points_y.append(
                    obj['coordinates']['y'])

            print(len(self.data_points_x))
            if len(self.data_points_x) >= self.data_process_size:
                if self.hist2d is None:
                    print("making new hist")
                    self.hist2d, self.xedges, self.yedges = np.histogram2d(
                        self.data_points_x,
                        self.data_points_y,
                        (self.xedges, self.yedges))
                else:
                    print("updating old hist")
                    self.hist2d += np.histogram2d(
                        self.data_points_x,
                        self.data_points_y,
                        (self.xedges, self.yedges))[0]
                    print(self.hist2d)

                extent = [self.xedges[0], self.xedges[-1],
                          self.yedges[0], self.yedges[-1]]
                gaussian = gaussian_filter(self.hist2d.T, sigma=1)
                plt.plot(self.data_points_x,
                         self.data_points_y, 'k.', markersize=5)
                # plt.clf()
                plt.imshow(gaussian, extent=extent,
                           origin='lower', cmap=plt.cm.jet)
                plt.show()

                self.data_points_x = []
                self.data_points_y = []


active_processors = [
    HeatMapGenerator
]


class KafkaManager:
    """
    Handles the creation, deletion and updates of kafka consumers
    """
    consumers = {}
    processors = {}

    @classmethod
    async def create_consumers(cls):
        for ds_server in DS_SERVERS:
            topic = ds_server['topic']
            if topic not in cls.consumers:
                cls.consumers[topic] = KafkaConsumer(
                    bootstrap_servers=KAFKA_SERVER_IP,
                    group_id=ds_server['group_id'],
                    auto_offset_reset='latest',
                    enable_auto_commit=True,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8')))
                cls.consumers[topic].assign([TopicPartition(topic, 0)])
                cls.consumers[topic].seek_to_end()

                cls.processors[topic] = []
                for processor_type in active_processors:
                    cls.processors[topic].append(processor_type(topic))

    @classmethod
    async def run(cls):
        """
        Runs all consumers asyncronously
        """
        tasks = []
        for (topic, consumer) in cls.consumers.items():
            print("started topic: ", topic)
            task = threading.Thread(
                target=cls.consume_and_process, args=(
                    topic, consumer, cls.processors[topic]))
            task.start()
            tasks.append(task)

        for task in tasks:
            task.join()

    @classmethod
    def consume_and_process(cls, topic, consumer, processors):
        """
        Gets kafka msgs, processes them and sends them to associated
        django-channels group
        """
        try:
            for msg in consumer:
                for processor in processors:
                    processor(msg.value)

        except Exception as exc:
            print("Exception raised in kafka consumer: {}".format(exc))


asyncio.get_event_loop().run_until_complete(KafkaManager.create_consumers())
asyncio.get_event_loop().run_until_complete(KafkaManager.run())
