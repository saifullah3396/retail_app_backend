"""
Defines a websocket consumer for handling incoming connections
"""
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework import status

from kafka_interface.kafka_consumer import KAFKA_GROUP_ID, AppKafkaConsumer
from kafka_interface.utils import CommandType

CONSUMER_STATE_INIT = {
    "streaming": False,
    "camera_ids": []
}


class KafkaStreamerConsumer(AsyncWebsocketConsumer):
    """
    Defines a django channels consumer for sending msgs received by kafka to
    the clients
    """

    async def connect(self):
        self.CMD_TO_FN_MAP = {
            CommandType.START_STREAMING: self.cmd_start_streaming,
            CommandType.STOP_STREAMING: self.cmd_stop_streaming,
            CommandType.CHANGE_CAMERA_IDS: self.cmd_change_camera_ids
        }

        self.state = CONSUMER_STATE_INIT.copy()

        await self.channel_layer.group_add(
            KAFKA_GROUP_ID,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def send_response(self, status, data={}, error={}):
        if bool(data):
            await self.send(text_data=json.dumps({
                "status": status,
                "data": data
            }))
        elif bool(error):
            await self.send(text_data=json.dumps({
                "status": status,
                "error": error
            }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        if await self.validate_data(data):
            command = data['command']
            if command in self.CMD_TO_FN_MAP:
                await self.CMD_TO_FN_MAP[command](data)

    async def validate_data(self, data):
        if 'command' not in data:
            await self.send_response(
                status.HTTP_400_BAD_REQUEST,
                error={"command": "Field is required."}
            )
            return False

        if data['command'] == CommandType.START_STREAMING or \
                data['command'] == CommandType.CHANGE_CAMERA_IDS:
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
        self.state['streaming'] = True
        self.state['camera_ids'] = data['camera_ids']
        await self.send_response(
            status.HTTP_200_OK,
            data=self.state
        )

    async def cmd_stop_streaming(self, data):
        self.state['streaming'] = False
        await self.send_response(
            status.HTTP_200_OK,
            data=self.state
        )

    async def cmd_change_camera_ids(self, data):
        self.state['camera_ids'] = data['camera_ids']
        await self.send_response(
            status.HTTP_200_OK,
            data=self.state
        )

    async def kafka_msg_update(self, event):
        message = event['message']
        if self.state['streaming'] and \
                message['id'] in self.state['camera_ids']:
            await self.send_response(
                status.HTTP_200_OK,
                data={                
                    "streamed_data": message
                }
            )


kafka_consumer = AppKafkaConsumer()
kafka_consumer.init_thread()
