# bot.py
import re
import time
from typing import Union, Optional

import asyncio
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, At, Plain
from aiocqhttp import CQHttp, Event, MessageSegment
from graia.ariadne.message.parser.base import DetectPrefix
from graia.broadcast import ExecutionStop

import constants
from constants import config, botManager
from manager.bot import BotManager
from universal import handle_message
from middlewares.ratelimit import manager as ratelimit_manager

bot = CQHttp()

class MentionMe:
    """At 账号或者提到账号群昵称"""

    def __init__(self, name: Union[bool, str] = True) -> None:
        self.name = name

    async def __call__(self, chain: MessageChain, event: Event) -> Optional[MessageChain]:
        first = chain[0]
        if isinstance(first, At) and first.target == config.onebot.qq:
            return MessageChain(chain.__root__[1:], inline=True).removeprefix(" ")
        elif isinstance(first, Plain):
            member_info = await bot.get_group_member_info(group_id=event.group_id, user_id=config.onebot.qq)
            if member_info.get("nickname") and chain.startswith(member_info.get("nickname")):
                return chain.removeprefix(" ")
        raise ExecutionStop


# TODO: use MessageSegment
# https://github.com/nonebot/aiocqhttp/blob/master/docs/common-topics.md
def transform_message_chain(text: str) -> MessageChain:
    pattern = r"\[CQ:(\w+),([^\]]+)\]"
    matches = re.finditer(pattern, text)

    message_classes = {
        "text": Plain,
        "image": Image,
        "at": At,
        # Add more message classes here
    }

    messages = []
    start = 0
    for match in matches:
        cq_type, params_str = match.groups()
        params = dict(re.findall(r"(\w+)=([^,]+)", params_str))
        message_class = message_classes.get(cq_type)
        if message_class:
            text_segment = text[start:match.start()]
            if text_segment:
                messages.append(Plain(text_segment))
            if cq_type == "at":
                params["target"] = int(params.pop("qq"))
            messages.append(message_class(**params))
            start = match.end()
    # Append any remaining plain text
    text_segment = text[start:]
    if text_segment:
        messages.append(Plain(text_segment))

    message_chain = MessageChain(*messages)
    return message_chain


FriendTrigger = DetectPrefix(config.trigger.prefix + config.trigger.prefix_friend)


@bot.on_message('private')
async def _(event: Event):
    if event.message.startswith('.'):
        return
    chain = transform_message_chain(event.message)
    try:
        msg = await FriendTrigger(chain, None)
    except:
        return

    async def response(resp):
        if isinstance(resp, Image):
            return await bot.send(event, MessageSegment.image(f"base64://{resp.base64}"))
        if config.response.quote:
            resp = MessageSegment.reply(event.message_id) + resp
        await bot.send(event, resp)

    try:
        await handle_message(
            response,
            f"friend-{event.user_id}",
            msg.display,
            chain,
            is_manager=event.user_id == config.onebot.manager_qq
        )
    except Exception as e:
        print(e)


GroupTrigger = [MentionMe(config.trigger.require_mention != "at"), DetectPrefix(
    config.trigger.prefix + config.trigger.prefix_group)] if config.trigger.require_mention != "none" else [
    DetectPrefix(config.trigger.prefix)]


@bot.on_message('group')
async def _(event: Event):
    if event.message.startswith('.'):
        return
    chain = transform_message_chain(event.message)
    try:
        for it in GroupTrigger:
            chain = await it(chain, event)
    except:
        return

    async def response(resp):
        if isinstance(resp, Image):
            return await bot.send(event, MessageSegment.image(f"base64://{resp.base64}"))
        if config.response.quote:
            resp = MessageSegment.reply(event.message_id) + resp
        await bot.send(event, resp)

    await handle_message(
        response,
        f"group-{event.group_id}",
        chain.display,
        is_manager=event.user_id == config.onebot.manager_qq
    )


@bot.on_message()
async def _(event: Event):
    if not event.message == ".重新加载配置文件":
        return
    if not event.user_id == config.onebot.manager_qq:
        return await bot.send(event, "您没有权限执行这个操作")
    constants.config = config.load_config()
    config.scan_presets()
    await bot.send(event, "配置文件重新载入完毕！")
    await bot.send(event, "重新登录账号中，详情请看控制台日志……")
    constants.botManager = BotManager(config)
    await botManager.login()
    await bot.send(event, "登录结束")


@bot.on_message()
async def _(event: Event):
    pattern = r"\.设置\s+(\w+)\s+(\S+)\s+额度为\s+(\d+)\s+条/小时"
    match = re.match(pattern, event.message.strip())
    if not match:
        return
    if not event.user_id == config.onebot.manager_qq:
        return await bot.send(event, "您没有权限执行这个操作")
    msg_type, msg_id, rate = match.groups()
    rate = int(rate)

    if msg_type != "群组" and msg_type != "好友":
        return await bot.send(event, "类型异常，仅支持设定【群组】或【好友】的额度")
    if msg_id != '默认' and not msg_id.isdecimal():
        return await bot.send(event, "目标异常，仅支持设定【默认】或【指定 QQ（群）号】的额度")
    ratelimit_manager.update(msg_type, msg_id, rate)
    return await bot.send(event, "额度更新成功！")


@bot.on_message()
async def _(event: Event):
    pattern = r"\.查看\s+(\w+)\s+(\S+)\s+的使用情况"
    match = re.match(pattern, event.message.strip())
    if not match:
        return

    msg_type, msg_id = match.groups()

    if msg_type != "群组" and msg_type != "好友":
        return await bot.send(event, "类型异常，仅支持设定【群组】或【好友】的额度")
    if msg_id != '默认' and not msg_id.isdecimal():
        return await bot.send(event, "目标异常，仅支持设定【默认】或【指定 QQ（群）号】的额度")
    limit = ratelimit_manager.get_limit(msg_type, msg_id)
    if limit is None:
        return await bot.send(event, f"{msg_type} {msg_id} 没有额度限制。")
    usage = ratelimit_manager.get_usage(msg_type, msg_id)
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    return await bot.send(event,
                          f"{msg_type} {msg_id} 的额度使用情况：{limit['rate']}条/小时， 当前已发送：{usage['count']}条消息\n整点重置，当前服务器时间：{current_time}")


@bot.on_message()
async def _(event: Event):
    pattern = ".查询API余额"
    if not event.message.strip() == pattern:
        return
    if not event.user_id == config.onebot.manager_qq:
        return await bot.send(event, "您没有权限执行这个操作")
    tasklist = []
    bots = botManager.bots.get("openai-api", [])
    for account in bots:
        tasklist.append(botManager.check_api_info(account))
    msg = await bot.send(event, "查询中，请稍等……")

    nodes = []
    for account, r in zip(bots, await asyncio.gather(*tasklist)):
        grant_used, grant_available, has_payment_method, total_usage, hard_limit_usd = r
        total_available = grant_available
        if has_payment_method:
            total_available = total_available + hard_limit_usd - total_usage
        answer = '' + account.api_key[:6] + "**" + account.api_key[-3:] + '\n'
        answer = answer + f' - 本月已用: {round(total_usage, 2)}$\n' \
                          f' - 可用：{round(total_available, 2)}$\n' \
                          f' - 绑卡：{has_payment_method}'
        node = MessageSegment.node_custom(event.self_id, "ChatGPT", answer)
        nodes.append(node)
    if len(nodes) == 0:
        await bot.send(event, "没有查询到任何 API！")
        return
    if event.group_id:
        await bot.call_action("send_group_forward_msg", group_id=event.group_id, messages=nodes)
    else:
        await bot.call_action("send_private_forward_msg", user_id=event.user_id, messages=nodes)


@bot.on_startup
async def startup():
    await botManager.login()


bot.run(host=config.onebot.reverse_ws_host, port=config.onebot.reverse_ws_port)
