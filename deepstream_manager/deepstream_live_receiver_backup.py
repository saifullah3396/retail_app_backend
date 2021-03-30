"""
Defines a websocket consumer for handling incoming connections
"""
import asyncio
import json

import aio_pika
from channels.generic.http import AsyncHttpConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework import status

from deepstream_manager.message_processors import *

active_processors = [
    DeepstreamFrontendStreamerCallbackInterface,
    # DeepstreamLiveHeatMapGenerator
]


class DeepstreamBackendStreamer(AsyncHttpConsumer):
    """
    A django channels consumer for receiving msgs from our deepstream servers
    which is then updated in local rabbitmq database.
    """

    async def handle(self, body):
        """
        Starts a asynchronous rabbitmq connection for incoming msgs from the
        deepstream servers published to local rabbitmq servers.
        """
        # get the group_id name from the url. In our case group_id name at
        # which the msgs are published will be equal to the uuid of the block
        # with which the deepstream server is associated.
        group_id = self.scope["url_route"]["kwargs"]["group_id"]

        # @todo: validate group_id here from block_ids in database

        # setup message processors
        self.processors = []
        for processor_type in active_processors:
            self.processors.append(processor_type(group_id))

        # make an asynchronous connection to amqp server
        connection = await aio_pika.connect_robust(
            "amqp://guest:guest@127.0.0.1/")

        # make the channel connection
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=100)

        # setup the amqp queue
        queue = await channel.declare_queue(
            exclusive=True, auto_delete=True)
        await queue.bind(exchange='amq.topic', routing_key=group_id)

        # start consuming messages from the deepstream servers recevied on
        # group_id
        await queue.consume(self.process_message)

    async def process_message(self, message):
        async with message.process():
            for processor in self.processors:
                await processor(message.body.decode())
            await asyncio.sleep(1)
