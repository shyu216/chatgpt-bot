import os
import sys
sys.path.append(os.getcwd())

import websockets

import asyncio
from universal import handle_message
from loguru import logger

from constants import botManager



async def handle_connection(websocket):

    req = await websocket.recv()

    name,msg,is_manager=req.split(":::")
    is_manager=bool(is_manager)

    logger.info(f"recv: {msg}")

    async def response(msg: str, websocket=websocket):

        # one socket connection can only has one send
        # may improve in the future
        if "我还在" in msg:
            logger.info(msg)
            return
        
        await websocket.send(msg)

        logger.info(f"send: {msg}")

    await handle_message(response, name, msg, is_manager=is_manager)


async def main():
    try:
        logger.info("OpenAI 服务器登录中……")
        await botManager.login()
    except:
        logger.error("OpenAI 服务器登录失败！")
        exit(-1)

    logger.info("Websocket 服务器即将启动！Listining on port 14514")
    async with websockets.serve(handle_connection, "localhost", 14514):

        await asyncio.Future()  # run forever


if __name__ == "__main__":

    asyncio.run(main())