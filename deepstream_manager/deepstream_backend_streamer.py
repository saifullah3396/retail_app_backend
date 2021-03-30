"""
Defines a websocket consumer for handling incoming connections from distributed
Deepstream servers
"""
import asyncio
import json
import time
import warnings

import aio_pika
from channels.generic.http import AsyncHttpConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from rest_framework import status

from deepstream_manager.message_processors import *
from deepstream_manager.utils import DeepstreamBackendStreamerCommands as DBSC

# currently active processing functionality for incoming live messages
ACTIVE_MESSAGE_PROCESSORS = [
    DeepstreamFrontendStreamerCallbackInterface,
    # DeepstreamLiveHeatMapGenerator
]

# default initial state of the connection with deepstream servers
SERVER_STATE_INIT = {
    'alive': False,
    'addr': None,
}


class DeepstreamBackendStreamer(AsyncWebsocketConsumer):
    """
    A django channels consumer for sending/receiving msgs from the deepstream
    servers for handling their state and configuration dynamically and also
    handling amqp consumers for live data transmission.
    """

    async def connect(self):
        """
        Handles incoming websocket connections.
        """

        # define command response callback map
        self.CMD_RESPONSE_CB_MAP = {
            DBSC.SEND_ADDR: self.cmd_send_addr_response_cb,
            DBSC.SEND_DIAGNOSTICS: self.cmd_send_diagnostics_response_cb,
        }

        self.CMD_TO_FN_MAP = {
            DBSC.SEND_ADDR: self.generate_cmd_send_addr,
            DBSC.SEND_DIAGNOSTICS: self.generate_cmd_send_diagnostics,
        }

        # initialize state of the server to default
        self.state = SERVER_STATE_INIT.copy()

        # accept the connection
        await self.accept()
        await self.CMD_TO_FN_MAP.get(DBSC.SEND_ADDR)()

    async def disconnect(self, close_code):
        """
        Gets called when the client is disconnected.
        """
        print(
            "Disconnected from the server at address: {}".format(
                self.state['addr']))

    async def send_command(self, command, data={}):
        """
        Sends a command JSON object to the deepstream server.
        """

        if bool(data):
            # if there is data, only send data to the websocket client
            await self.send(text_data=json.dumps({
                "command": command,
                "data": data
            }))
        else:
            await self.send(text_data=json.dumps({
                "command": command
            }))

    async def receive(self, text_data):
        """
        Handles the data received from the deepstream server
        """

        data = json.loads(text_data)
        if await self.validate_data(data):
            cmd_response_cb_fn = self.CMD_RESPONSE_CB_MAP.get(data['command'])
            if cmd_response_cb_fn:
                await cmd_response_cb_fn(data)

    async def validate_data(self, data):
        """
        Validates the data received from the deepstream server
        """

        # check if command exists in the data
        if 'command' not in data:
            warnings.warn(
                "Invalid data received from the deepstream server: "
                "{}".format(),
                UserWarning)
            return False

        if not self.state['alive']:
            # make sure the server address is recieved before any other kind of
            # operation. Only recieve send_addr response until server is alive.
            if data['command'] != DBSC.SEND_ADDR:
                warnings.warn(
                    "Server must send its address to operate",
                    UserWarning)
                return False

            if 'addr' not in data:
                warnings.warn(
                    "addr: Field required.",
                    UserWarning)
                return False
        else:
            # server is alive
            if data['command'] == DBSC.SEND_DIAGNOSTICS and \
                    'server_state' not in data:
                warnings.warn(
                    "No state received from the deepstream server: {}".format(
                        self.state['addr']),
                    UserWarning)
                return False

        return True

    async def cmd_send_addr_response_cb(self, data):
        """
        Callback for response received from the server when the command
        SEND_ADDR is sent.
        """

        if not self.state['alive']:
            # connection established
            self.state['alive'] = True
            self.state['addr'] = data['addr']

            print(
                "Connection established with the "
                "server at address: {}".format(self.state['addr']))

    async def cmd_send_diagnostics_response_cb(self, data):
        """
        Callback for response received from the server when the command
        SEND_DIAGNOSTICS is sent.
        """

        if self.state['alive']:
            self.state['server_state'] = data['server_state']

    async def deepstream_generate_command(self, event):
        """
        Gets called whenever a command is received for this server from
        anywhere across the django server
        """
        event = json.loads(event)
        if self.state['alive']:
            await self.CMD_TO_FN_MAP(event['command'])(event['data'])

    async def generate_cmd_send_addr(self, data={}):
        """
        Generates a command for the server corresponding to SEND_DIAGNOSTICS
        """
        await self.send_command(DBSC.SEND_ADDR)

    async def generate_cmd_send_diagnostics(self, data):
        """
        Generates a command for the server corresponding to SEND_DIAGNOSTICS.
        """

        if self.state['alive']:
            await self.send_command(DBSC.SEND_DIAGNOSTICS)

    async def init_amqp_consumer(self, event):
        # get the group_id from the url. Group id in our case would be the
        # uuid of the respective block the client is watching
        self.group_id = self.scope['url_route']['kwargs']['group_id']

        # setup message processors for live incoming data
        self.processors = []
        for processor_type in ACTIVE_MESSAGE_PROCESSORS:
            self.processors.append(processor_type(self.group_id))

        # make an asynchronous connection to amqp server
        connection = await aio_pika.connect_robust(
            "amqp://guest:guest@127.0.0.1/")

        # make the channel connection
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=100)

        # setup the amqp queue
        queue = await channel.declare_queue(
            exclusive=True, auto_delete=True)
        await queue.bind(exchange='amq.topic', routing_key=self.group_id)

        # start consuming messages from the deepstream servers recevied on
        # group_id
        await queue.consume(self.process_amqp_message)

    async def process_amqp_message(self, message):
        async with message.process():
            for processor in self.processors:
                await processor(message.body.decode())
            await asyncio.sleep(1)
