"""
Defines the utilities used in websocket send/recieve operations.
"""
from enum import IntEnum


class DeepstreamFrontendStreamerCommands(IntEnum):
    STOP_STREAMING = 0
    START_STREAMING = 1
    CHANGE_CAMERA_IDS = 2


class DeepstreamBackendStreamerMsgProtocol(IntEnum):
    SEND_ADDR = 0
    SEND_DIAGNOSTICS = 1
    UPDATE_CONFIG = 2
    STOP_STREAMING = 3
    START_STREAMING = 4
