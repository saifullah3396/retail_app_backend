"""
Defines the utilities used in websocket send/recieve operations.
"""
from enum import IntEnum


class CommandType(IntEnum):
    STOP_STREAMING = 0
    START_STREAMING = 1
    CHANGE_CAMERA_IDS = 2
