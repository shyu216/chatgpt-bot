
import asyncio
import websockets

from loguru import logger

from typing import Callable
from graia.ariadne.message.chain import MessageChain

async def handle_client(respond: Callable, session_id: str, message: str, chain: MessageChain = MessageChain("Unsupported"), is_manager: bool = False):
    uri="ws://localhost:14514"

    try:
        async with websockets.connect(uri) as websocket:

            msg=f"{session_id}:::{message}:::{is_manager}"

            await websocket.send(msg)

            logger.info(f"send: {msg}")

            resp=await websocket.recv()

            logger.info(f"recv: {resp}")

            await respond(resp)

    except Exception as e:
        logger.error(e)

    

async def demo():

    uri = "ws://localhost:14514"

    async with websockets.connect(uri) as websocket:

        msg=f"friend-test:::你好:::False"

        await websocket.send(msg)

        logger.info(f"send: {msg}")

        resp=await websocket.recv()

        logger.info(f"recv: {resp}")


if __name__ == "__main__":

    asyncio.run(demo())