"""
Defines a websocket consumer for handling incoming connections from distributed
Deepstream servers
"""
import asyncio
import json
import logging
import re

import aio_pika
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from rest_framework import status

from backend.settings import (AMQP_EXCHANGE, AMQP_PASSWORD,
                              AMQP_SERVER_ADDRESS, AMQP_SERVER_PORT,
                              AMQP_SERVER_VHOST, AMQP_USER)
from deepstream_manager import queries
from deepstream_manager.message_processors import \
    DeepstreamFrontendStreamerCallbackInterface
from deepstream_manager.utils import \
    DeepstreamBackendStreamerMsgProtocol as MessageProtocol
from deepstream_servers.models import DeepstreamServer

input_request_logger = logging.getLogger(
    'deepstream_manager_input_request_logger')
output_request_logger = logging.getLogger(
    'deepstream_manager_output_request_logger')


# currently active processing functionality for incoming live messages
ACTIVE_MESSAGE_PROCESSORS = [
    DeepstreamFrontendStreamerCallbackInterface,
]

# default initial state of the connection with deepstream servers
SERVER_STATE_INIT = {
    'alive': False,
    'server_id': None,
    'server_group_id': None
}


class DeepstreamBackendStreamer(AsyncWebsocketConsumer):
    """
    A django channels consumer for sending/receiving msgs from the deepstream
    servers for handling their state and configuration dynamically and also
    handling amqp consumers for live data transmission.
    """

    # pylint: disable=attribute-defined-outside-init
    async def connect(self):
        """
        Handles incoming websocket connections.
        """

        # map send functions to msg protocols
        self.cmd_to_fn_map = {
            MessageProtocol.SEND_ADDR:
                self.generate_cmd_send_addr,
            MessageProtocol.SEND_DIAGNOSTICS:
                self.generate_cmd_send_diagnostics,
            MessageProtocol.UPDATE_CONFIG:
                self.generate_cmd_update_config,
            MessageProtocol.STOP_STREAMING:
                self.generate_cmd_stop_streaming,
            MessageProtocol.START_STREAMING:
                self.generate_cmd_start_streaming,
        }

        # map response callback functions to msg protocols
        self.cmd_response_cb_map = {
            MessageProtocol.SEND_ADDR:
                self.cmd_send_addr_response_cb,
            MessageProtocol.SEND_DIAGNOSTICS:
                self.cmd_send_diagnostics_response_cb,
            MessageProtocol.UPDATE_CONFIG:
                self.cmd_update_config_response_cb,
            MessageProtocol.STOP_STREAMING:
                self.cmd_stop_streaming_response_cb,
            MessageProtocol.START_STREAMING:
                self.cmd_start_streaming_response_cb,
        }

        # initialize state of the server to default
        self.state = SERVER_STATE_INIT.copy()

        # initialize logging extra fields
        self.logging_extra = {
            'conn_protocol': 'WebSocket',
            'request': 'SEND/RECEIVE',
            'url': 'deepstream/server/',
            'client': self.scope['client']
        }

        # accept the connection
        await self.accept()
        await self.cmd_to_fn_map.get(MessageProtocol.SEND_ADDR)()

    async def disconnect(self, code):
        """
        Gets called when the client is disconnected.
        """

    async def send_response(self, status_code, data=None, error=None):
        """
        Sends a response JSON object to the deepstream server.
        """

        if data:
            # if there is data, only send data to the websocket client
            await self.send(text_data=json.dumps({
                "status": status_code,
                "data": data
            }))
        elif error:
            # if there is error send error to the websocket client
            await self.send(text_data=json.dumps({
                "status": status_code,
                "error": error
            }))
        else:
            await self.send(text_data=json.dumps({
                "status": status_code
            }))

    async def send_command(self, msg_protocol, data=None):
        """
        Sends a command JSON object to the deepstream server.
        """

        if data:
            # if there is data, only send data to the websocket client
            await self.send(text_data=json.dumps({
                "msg_protocol": msg_protocol,
                "data": data
            }))
        else:
            await self.send(text_data=json.dumps({
                "msg_protocol": msg_protocol
            }))

    async def receive(self, text_data=None, bytes_data=None):
        """
        Handles the data received from the deepstream server
        """

        try:
            data = json.loads(text_data)
            if await self.validate_data(data):
                msg_protocol = MessageProtocol(data['msg_protocol'])

                cmd_response_cb_fn = \
                    self.cmd_response_cb_map.get(msg_protocol)
                if cmd_response_cb_fn:
                    await cmd_response_cb_fn(data)

        # pylint: disable=broad-except
        except Exception as exc:
            input_request_logger.error(
                'Exception raised: %s', exc,
                extra={
                    **self.logging_extra,
                    'status': status.HTTP_400_BAD_REQUEST,
                    'msg_protocol': msg_protocol,
                })
            await self.send_response(
                status.HTTP_400_BAD_REQUEST,
                error="Could not process request."
            )

    async def validate_data(self, data):
        """
        Validates the data received from the deepstream server
        """

        # validate data schema, it must have status and msg type
        response_status = status.HTTP_400_BAD_REQUEST

        # make sure status is received
        if 'status' not in data:
            input_request_logger.error(
                'Invalid response object received.',
                extra={
                    **self.logging_extra,
                    'status': '',
                    'msg_protocol': '',
                })

            await self.send_response(
                response_status,
                error={
                    'status': 'Field required.'}
            )
            return False

        # check if we got bad request as response
        if data['status'] == status.HTTP_400_BAD_REQUEST:
            # check if we got any error related to send 'msg_protocol'
            if 'error' in data and 'msg_protocol' in data['error']:
                self.log_error(data, '')
                return False

        # make sure msg_protocol exists in response
        if 'msg_protocol' not in data:
            input_request_logger.error(
                'Invalid response object received.',
                extra={
                    **self.logging_extra,
                    'status': '',
                    'msg_protocol': '',
                })

            await self.send_response(
                response_status,
                error={
                    "msg_protocol":
                    "Can only be of the following {}.".format(
                        list(map(int, MessageProtocol)))}
            )
            return False

        # check if valid msg protocol is present in data
        if data['msg_protocol'] not in list(map(int, MessageProtocol)):
            input_request_logger.error(
                'Invalid msg_protocol received.',
                extra={
                    **self.logging_extra,
                    'status': response_status,
                    'msg_protocol': '',
                })
            await self.send_response(
                response_status,
                error={
                    "msg_protocol":
                    "Can only be of the following {}.".format(
                        list(map(int, MessageProtocol)))}
            )
            return False

        msg_protocol = MessageProtocol(data['msg_protocol'])

        # if connection is not informed yet
        if not self.state['alive']:
            # make sure the server address is recieved before any other kind of
            # operation. Only recieve send_addr response until server is alive.
            if msg_protocol != MessageProtocol.SEND_ADDR:
                input_request_logger.error(
                    'No MAC address received from the deepstream server.',
                    extra={
                        **self.logging_extra,
                        'status': response_status,
                        'msg_protocol': msg_protocol,
                    })
                await self.send_response(
                    response_status,
                    error="Server must send its MAC address to operate"
                )
                return False

            if 'mac_addr' not in data:
                input_request_logger.error(
                    '',
                    extra={
                        **self.logging_extra,
                        'status': response_status,
                        'msg_protocol': msg_protocol,
                    })
                await self.send_response(
                    response_status,
                    error={"mac_addr": "Field is required."}
                )
                return False

            if not re.search(
                    '([0-9a-fA-F]{2}[:]){5}([0-9a-fA-F]{2})', data['mac_addr']):
                input_request_logger.error(
                    '',
                    extra={
                        **self.logging_extra,
                        'status': response_status,
                        'msg_protocol': msg_protocol,
                    })
                await self.send_response(
                    response_status,
                    error={"mac_addr": "MAC address is invalid."}
                )
                return False

        else:
            # server is alive
            if msg_protocol == MessageProtocol.SEND_DIAGNOSTICS and \
                    'diagnostics_info' not in data:
                input_request_logger.error(
                    '',
                    extra={
                        **self.logging_extra,
                        'status': response_status,
                        'msg_protocol': msg_protocol,
                    })
                await self.send_response(
                    response_status,
                    error={"diagnostics_info": "Field is required."}
                )
                return False

            elif msg_protocol == MessageProtocol.START_STREAMING:
                if 'stream_info' not in data:
                    input_request_logger.error(
                        '',
                        extra={
                            **self.logging_extra,
                            'status': response_status,
                            'msg_protocol': msg_protocol,
                        })
                    await self.send_response(
                        response_status,
                        error={"stream_info": "Field is required."}
                    )
                    return False

                if 'routing_key' not in data['stream_info']:
                    input_request_logger.error(
                        '',
                        extra={
                            **self.logging_extra,
                            'status': response_status,
                            'msg_protocol': msg_protocol,
                        })
                    await self.send_response(
                        response_status,
                        error={
                            "stream_info": {
                                "routing_key": "Field is required."
                            }}
                    )
                    return False

        return True

    async def cmd_send_addr_response_cb(self, data):
        """
        Callback for response received from the server when the command
        SEND_ADDR is sent.
        """

        received_status = data['status']
        if received_status == status.HTTP_200_OK:
            if not self.state['alive']:
                # connection established
                self.state['alive'] = True

                # get the deepstream server associated with the mac address
                deepstream_server = await database_sync_to_async(
                    queries.get_deepstream_server)(data['mac_addr'])
                self.state['server_id'] = deepstream_server.id
                self.state['server_group_id'] = await database_sync_to_async(
                    queries.get_deepstream_server_block_id)(deepstream_server)

                if deepstream_server:
                    input_request_logger.info(
                        "Deepstream server validated.",
                        extra={
                            **self.logging_extra,
                            'status': status.HTTP_200_OK,
                            'msg_protocol': data['msg_protocol'],
                        })

                    # update the server configuration from actual connected
                    # server in db
                    deepstream_server.ip_addr = \
                        self.scope['client'][0] + ':' + \
                        str(self.scope['client'][1])
                    current_time = timezone.now()
                    deepstream_server.status = DeepstreamServer.ONLINE
                    deepstream_server.connected_at = current_time
                    deepstream_server.last_response_received_at = current_time
                    await database_sync_to_async(
                        queries.save_deepstream_server)(deepstream_server)

                    # add a log entry to the database regarding connection
                    await self.log_to_database(
                        "Connection made with the server.")

                    # send the configuration of this server added in database
                    # to the server for initialization
                    await self.generate_cmd_update_config()
                else:
                    input_request_logger.info(
                        "Deepstream server [%s] invalidated.",
                        data['mac_addr'],
                        extra={
                            **self.logging_extra,
                            'status': status.HTTP_200_OK,
                            'msg_protocol': data['msg_protocol'],
                        })
                    await self.send_response(
                        status.HTTP_400_BAD_REQUEST,
                        error={
                            "mac_addr": "MAC address not registered as a "
                            "deepstream server."}
                    )
        else:
            self.log_error(
                data,
                MessageProtocol.SEND_ADDR,
                log_to_database=True,
                error_message_prefix="Error raised while fetching MAC address "
                "from the server.")

    async def cmd_send_diagnostics_response_cb(self, data):
        """
        Callback for response received from the server when the command
        SEND_DIAGNOSTICS is sent.
        """

        if data['status'] == status.HTTP_200_OK:
            if self.state['alive']:
                await self.log_to_database(
                    "Diagnostics information received from the server.")
                self.state['diagnostics_info'] = data['diagnostics_info']
        else:
            self.log_error(
                data,
                MessageProtocol.SEND_DIAGNOSTICS,
                log_to_database=True,
                error_message_prefix="Error raised while fetching diagnostics "
                "info from the server:")

    async def cmd_update_config_response_cb(self, data):
        """
        Callback for response received from the server when the command
        UPDATE_CONFIG is sent.
        """

        if data['status'] == status.HTTP_200_OK:
            if self.state['alive']:
                await self.log_to_database(
                    "Deepstream configuration successfully updated:")

                # send the start streaming command once the configuration is
                # successfully
                await self.generate_cmd_start_streaming()
        else:
            self.log_error(
                data,
                MessageProtocol.UPDATE_CONFIG,
                log_to_database=True,
                error_message_prefix="Error raised while updating deepstream "
                "configuration to the server:")

    async def cmd_start_streaming_response_cb(self, data):
        """
        Callback for response received from the server when the command
        START_STREAMING is sent.
        """

        if data['status'] == status.HTTP_200_OK:
            if self.state['alive']:
                await self.log_to_database("Deepstream pipeline started.")

            # start consuming msgs from the started stream
            try:
                await self.init_amqp_consumer(
                    data['stream_info']['routing_key'],
                    str(self.state['server_group_id']))

            except aio_pika.exceptions.AMQPError:
                # if there is some issue in initializing amqp consumer, send
                # stop streaming command to server
                await self.log_to_database(
                    "Failed to initialize amqp consumer for streamed data.")
                await self.generate_cmd_stop_streaming()
        else:
            self.log_error(
                data,
                MessageProtocol.START_STREAMING,
                log_to_database=True,
                error_message_prefix="Error raised while starting deepstream:")

    async def cmd_stop_streaming_response_cb(self, data):
        """
        Callback for response received from the server when the command
        STOP_STREAMING is sent.
        """

        if data['status'] == status.HTTP_200_OK:
            if self.state['alive']:
                await self.log_to_database("Deepstream pipeline stopped.")
        else:
            self.log_error(
                data,
                MessageProtocol.START_STREAMING,
                log_to_database=True,
                error_message_prefix="Error raised while stopping deepstream:")

    async def deepstream_generate_command(self, event):
        """
        Gets called whenever a command is received for this server from
        anywhere across the django server
        """
        event = json.loads(event)
        if self.state['alive']:
            await self.cmd_to_fn_map.get(event['msg_protocol'])(event['data'])

    async def generate_cmd_send_addr(self, data=None):
        # pylint: disable=unused-argument
        """
        Generates a command for the server corresponding to SEND_DIAGNOSTICS
        """
        await self.send_command(MessageProtocol.SEND_ADDR)

    async def generate_cmd_send_diagnostics(self, data=None):
        # pylint: disable=unused-argument
        """
        Generates a command for the server corresponding to SEND_DIAGNOSTICS.
        """

        if self.state['alive']:
            await self.log_to_database(
                "Requesting diagnostics information from the server...")
            await self.send_command(MessageProtocol.SEND_DIAGNOSTICS)

    async def generate_cmd_update_config(self, data=None):
        # pylint: disable=unused-argument
        """
        Generates a command for the server corresponding to UPDATE_CONFIG.
        """

        if self.state['alive']:
            # fetch all the cameras associated with this server

            await self.log_to_database("Updating deepstream configuration...")
            deepstream_config = await database_sync_to_async(
                queries.generate_deepstream_config)(
                self.state['server_id'])
            if deepstream_config:
                await self.send_command(
                    MessageProtocol.UPDATE_CONFIG, data=deepstream_config)
            else:
                await self.log_to_database(
                    "Failed to generate deepstream configuration.")

    async def generate_cmd_start_streaming(self, data=None):
        # pylint: disable=unused-argument
        """
        Generates a command for the server corresponding to START_STREAMING.
        """

        if self.state['alive']:
            await self.log_to_database("Starting deepstream pipeline...")
            await self.send_command(MessageProtocol.START_STREAMING)

    async def generate_cmd_stop_streaming(self, data=None):
        # pylint: disable=unused-argument
        """
        Generates a command for the server corresponding to STOP_STREAMING.
        """

        if self.state['alive']:
            await self.log_to_database("Stopping deepstream pipeline...")
            await self.send_command(MessageProtocol.STOP_STREAMING)

            # close msg consuming as well
            await self.close_amqp_consumer()

    def log_error(
            self,
            data,
            msg_protocol,
            error_message_prefix="Error: ",
            log_to_database=False):
        """
        Generates an error message and logs it to database or logger.
        """

        error_message = error_message_prefix
        if 'error' in data:
            error_message += json.dumps({
                key: data[key] for key in ['status', 'error']
            })
        else:
            error_message += json.dumps({
                key: data[key] for key in ['status']
            })

        output_request_logger.error(
            error_message,
            extra={
                **self.logging_extra,
                'msg_protocol': msg_protocol,
            })

        if log_to_database:
            self.log_to_database(error_message)

    async def log_to_database(self, message):
        """
        Logs the given message to database
        """
        if self.state['server_id']:
            await database_sync_to_async(queries.create_deepstream_log_entry)(
                message, self.state['server_id'])

    async def init_amqp_consumer(self, routing_key, channels_group_id):
        """
        Initializes an amqp consumer for the given routing key and group id.
        """

        # setup message processors for live incoming data
        self.processors = []
        for processor_type in ACTIVE_MESSAGE_PROCESSORS:
            self.processors.append(processor_type(channels_group_id))

        # make an asynchronous connection to amqp server
        self.amqp_connection = await aio_pika.connect_robust(
            "amqp://{}:{}@{}:{}/{}".format(
                AMQP_USER,
                AMQP_PASSWORD,
                AMQP_SERVER_ADDRESS,
                AMQP_SERVER_PORT,
                AMQP_SERVER_VHOST))

        # make the channel connection
        channel = await self.amqp_connection.channel()
        await channel.set_qos(prefetch_count=100)

        # setup the amqp queue
        self.amqp_queue = await channel.declare_queue(
            exclusive=True, auto_delete=True)
        self.amqp_routing_key = routing_key
        await self.amqp_queue.bind(
            exchange=AMQP_EXCHANGE, routing_key=self.amqp_routing_key)

        # start consuming messages from the deepstream servers recevied on
        # group_id
        await self.amqp_queue.consume(self.process_amqp_message)

    async def process_amqp_message(self, message):
        """
        Message procesing callback for amqp consumer.
        """
        async with message.process():
            for processor in self.processors:
                await processor(message.body.decode())
            await asyncio.sleep(1)

    async def close_amqp_consumer(self):
        """
        Closes the amqp consumer
        """
        await self.amqp_queue.unbind(AMQP_EXCHANGE, self.amqp_routing_key)
        await self.amqp_queue.delete()
        await self.amqp_connection.close()
