"""
Defines a websocket consumer for handling incoming connections
"""
import json
import time

from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework import status

from deepstream_manager.utils import DeepstreamFrontendStreamerCommands as DFSC

CONSUMER_STATE_INIT = {
    "streaming": False,
    "camera_ids": []
}


class DeepstreamFrontendStreamer(AsyncWebsocketConsumer):
    """
    A django channels consumer for sending/receiving msgs from clients
    to handle streaming of live data to the clients.
    """

    async def connect(self):
        """
        Handles incoming websocket connections.
        """

        # initialize state to default
        self.state = CONSUMER_STATE_INIT.copy()

        # define command type to function map
        self.CMD_TO_FN_MAP = {
            DFSC.START_STREAMING: self.cmd_start_streaming,
            DFSC.STOP_STREAMING: self.cmd_stop_streaming,
            DFSC.CHANGE_CAMERA_IDS: self.cmd_change_camera_ids
        }

        # get the group_id from the url. Group id in our case would be the
        # uuid of the respective block the client is watching
        group_id = self.scope['url_route']['kwargs']['group_id']

        # @todo: validate group id here

        # connect the channel layer of this consumer to the required group id
        await self.channel_layer.group_add(
            group_id,
            self.channel_name
        )

        # accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        """
        Gets called when the client is disconnected.
        """
        pass

    async def send_response(self, status, data={}, error={}):
        """
        Sends a response JSON object to the frontend client.
        """

        if bool(data):
            # if there is data, only send data to the websocket client
            await self.send(text_data=json.dumps({
                "status": status,
                "data": data
            }))
        elif bool(error):
            # if there is error send error to the websocket client
            await self.send(text_data=json.dumps({
                "status": status,
                "error": error
            }))

    async def receive(self, text_data):
        """
        Validates the data received and performs the required action based on
        the input.
        """

        data = json.loads(text_data)
        if await self.validate_data(data):
            command = data['command']
            if command in self.CMD_TO_FN_MAP:
                await self.CMD_TO_FN_MAP[command](data)

    async def validate_data(self, data):
        """
        Validates the data received from the client and sends error response in
        case it is not valid.
        """

        if 'command' not in data:
            await self.send_response(
                status.HTTP_400_BAD_REQUEST,
                error={"command": "Field is required."}
            )
            return False

        if data['command'] == DFSC.START_STREAMING or \
                data['command'] == DFSC.CHANGE_CAMERA_IDS:
            if "camera_ids" not in data:
                await self.send_response(
                    status.HTTP_400_BAD_REQUEST,
                    error={"camera_ids": "Field is required."}
                )
                return False

            if not isinstance(data["camera_ids"], list):
                await self.send_response(
                    status.HTTP_400_BAD_REQUEST,
                    error={"camera_ids": "Field must be a list of ids."}
                )
                return False

        return True

    async def cmd_start_streaming(self, data):
        """
        Command for starting continuous data streaming on this connection based
        on input data.
        """

        self.state['streaming'] = True
        self.state['camera_ids'] = data['camera_ids']
        await self.send_response(
            status.HTTP_200_OK,
            data=self.state
        )

    async def cmd_stop_streaming(self, data):
        """
        Command for stopping data streaming on this connection based on input
        data.
        """

        self.state['streaming'] = False
        await self.send_response(
            status.HTTP_200_OK,
            data=self.state
        )

    async def cmd_change_camera_ids(self, data):
        """
        Command for changing streaming ids based on input data.
        """

        self.state['camera_ids'] = data['camera_ids']
        await self.send_response(
            status.HTTP_200_OK,
            data=self.state
        )

    async def deepstream_message_update(self, event):
        """
        Gets called whenever a new message is received from live deepstream
        update.
        """
        message_dict = json.loads(event['message'])
        if self.state['streaming'] and \
                message_dict['sensorId'] in self.state['camera_ids']:
            await self.send_response(
                status.HTTP_200_OK,
                data={
                    "streamed_data": event['message']
                }
            )
