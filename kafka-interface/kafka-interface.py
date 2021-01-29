from time import sleep
from json import dumps, loads
from kafka import KafkaConsumer
import asyncio
import websockets

KAFKA_STREAM_PORT = 8765
# to be taken from database for current view
cameras_to_handle = [0, 1, 2]

topic = 'detection'
detection_consumer = KafkaConsumer(
    topic,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='camera_events',
    value_deserializer=lambda x: loads(x.decode('utf-8')))

# remove all previous msgs
detection_consumer.poll()
detection_consumer.seek_to_end()


async def kafka_to_ws(websocket, path):
    for detection in detection_consumer:
        if detection.value['id'] in cameras_to_handle:
            # get the latest kafka msg and send it to websocket
            await websocket.send(dumps(detection.value).encode('utf-8'))

# start a web sockets server for sending data from kafka to websocket
start_server = websockets.serve(kafka_to_ws, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
