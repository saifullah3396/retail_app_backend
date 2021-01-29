#!/usr/bin/env python

import asyncio
import websockets


async def recv():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            msg = await websocket.recv()
            print(f"< {msg}")

asyncio.get_event_loop().run_until_complete(recv())
