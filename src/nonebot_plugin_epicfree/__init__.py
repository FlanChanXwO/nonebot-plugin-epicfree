from traceback import format_exc
from typing import Union, Dict

from nonebot import get_bot, get_driver, on_command, on_regex, require
from nonebot.adapters import Bot, Event
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Depends
from nonebot.plugin import PluginMetadata, get_plugin_config
from nonebot_plugin_localstore import get_plugin_data_file
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    PrivateMessageEvent,
    Message,
)

# 导入APScheduler插件
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

# 导入数据源和定时任务管理函数
from .data_source import (
    check_push,
    get_epic_free,
    subscribe_helper,
)
from .config import Config
from .proxy import init_proxy
from .schedule import scheduler_manage

# -------------------- 插件元数据 --------------------
__plugin_meta__ = PluginMetadata(
    name="Epic喜加一",
    description="定时推送 Epic Game Store 每周免费游戏信息",
    usage="""
    - `epic喜加一`: 手动获取本周免费游戏信息。
    - `epic订阅 8:30`: 在每天的8:30为本群/私聊开启推送。
    - `epic取消订阅`: 关闭本群/私聊的推送。
    - `epic订阅状态`: 查看本群/私聊的订阅状态和推送时间。
    (群聊中，指令需要管理员或主人权限)
    """,
    type="application",
    config=Config,
    homepage="https://github.com/FlanChanXwO/nonebot-plugin-epicfree",
    supported_adapters={"~onebot.v11"},
    extra={
            "authors": ["FlanChanXwO", "monsterxcn", "studylessshape"],
            "version": "0.2.7"
          },
)

# 配置
plugin_config = get_plugin_config(Config).epic

# -------------------- 指令定义 --------------------
epic_matcher = on_regex(r"^(epic)?喜(加|\+|＋)(一|1)$", priority=10, block=True)
sub_cmd = on_command("epic订阅", priority=10, block=True)
unsub_cmd = on_command("epic取消订阅", aliases={"取消epic订阅"}, priority=10, block=True)
status_cmd = on_command("epic订阅状态", aliases={"epic推送状态"}, priority=10, block=True)


# -------------------- 初始化 --------------------
@get_driver().on_startup
async def on_startup():
    init_proxy(plugin_config)


def get_job_id(event: Union[GroupMessageEvent, PrivateMessageEvent]) -> str:
    """根据事件类型生成唯一的 job_id"""
    if isinstance(event, GroupMessageEvent):
        return f"epic_group_{event.group_id}"
    else:
        return f"epic_private_{event.user_id}"


def get_sub_info(event: Union[GroupMessageEvent, PrivateMessageEvent]) -> dict:
    """根据事件类型获取订阅主体信息"""
    if isinstance(event, GroupMessageEvent):
        return {"sub_type": "群聊", "subject": str(event.group_id)}
    else:
        return {"sub_type": "私聊", "subject": str(event.user_id)}


async def permission_check(matcher: Matcher, event: Event) -> None:
    """检查群聊中的权限"""
    if isinstance(event, GroupMessageEvent) and plugin_config.superuser_only:
        is_superuser = str(event.user_id) in get_driver().config.superusers
        if not is_superuser and event.sender.role not in ["admin", "owner"]:
            await matcher.finish("只有群管理员和主人才能操作订阅哦~")


# -------------------- 指令处理 --------------------

# 手动获取
@epic_matcher.handle()
async def handle_epic_free(bot: Bot, event: Event):
    free_games = await get_epic_free()
    if isinstance(event, GroupMessageEvent):
        await bot.send_group_forward_msg(group_id=event.group_id, messages=free_games)
    else:
        await bot.send_private_forward_msg(user_id=event.user_id, messages=free_games)


# 开启订阅
@sub_cmd.handle(parameterless=[Depends(permission_check)])
async def handle_sub(matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent],
                     args: Message = CommandArg()):
    hour: int = 0
    minute: int = 0
    cron_time: str = ""
    arg_text = args.extract_plain_text().strip()
    if not arg_text:
        await matcher.finish("请提供订阅时间，格式为 `HH:MM`，例如 `epic订阅 8:30`")

    try:
        hour, minute = map(int, arg_text.split(':'))
        cron_time = f"{minute} {hour}"  # APScheduler cron format: min hour
    except ValueError:
        await matcher.finish("时间格式不正确！请使用 `HH:MM` 格式，例如 `epic订阅 8:30`")

    sub_info = get_sub_info(event)
    job_id = get_job_id(event)

    # 1. 更新订阅者列表
    await subscribe_helper(method="启用", **sub_info)
    # 2. 存储/更新定时任务配置
    await scheduler_manage(job_id=job_id, action="set", time=cron_time)
    # 3. 添加/更新 APScheduler 任务
    scheduler.add_job(
        push_epic_free, "cron", hour=hour, minute=minute, id=job_id, replace_existing=True,
        kwargs={"job_id": job_id, "sub_info": sub_info}
    )

    await matcher.finish(f"已成功为本{sub_info['sub_type']}开启 Epic 每日推送，时间：{hour:02d}:{minute:02d}")


# 取消订阅
@unsub_cmd.handle(parameterless=[Depends(permission_check)])
async def handle_unsub(matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent]):
    sub_info = get_sub_info(event)
    job_id = get_job_id(event)

    # 1. 从订阅者列表中删除
    await subscribe_helper(method="删除", **sub_info)
    # 2. 从定时任务配置中删除
    await scheduler_manage(job_id=job_id, action="delete")
    # 3. 从 APScheduler 中移除任务
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    await matcher.finish(f"已为本{sub_info['sub_type']}取消 Epic 每日推送。")


# 查看订阅状态
@status_cmd.handle()
async def handle_status(matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent]):
    sub_info = get_sub_info(event)
    job_id = get_job_id(event)

    # 检查是否在订阅列表中
    all_subs = await subscribe_helper(method="读取")
    if sub_info["subject"] not in all_subs.get(sub_info["sub_type"], []):
        await matcher.finish(f"本{sub_info['sub_type']}当前未订阅 Epic 推送。")
        return

    # 获取定时任务配置
    sched_info = await scheduler_manage(job_id=job_id, action="get")
    if sched_info:
        minute, hour = sched_info.split()
        await matcher.finish(f"本{sub_info['sub_type']}已订阅 Epic 推送，每日推送时间为：{hour}:{minute}")
    else:
        # 数据不一致的兼容处理
        await matcher.finish(f"本{sub_info['sub_type']}已订阅，但未找到推送时间设置。请使用 `epic取消订阅` 后重新订阅。")


# -------------------- 定时推送核心函数 --------------------

async def push_epic_free(job_id: str, sub_info: dict):
    """定时推送的执行函数"""
    bot = get_bot()
    logger.info(f"开始执行 Epic 推送任务: {job_id}")

    # 再次检查订阅状态，防止数据不一致
    all_subs = await subscribe_helper(method="读取")
    if sub_info["subject"] not in all_subs.get(sub_info["sub_type"], []):
        logger.warning(f"任务 {job_id} 启动，但目标 {sub_info['subject']} 已不在订阅列表，自动移除任务。")
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        return

    # 获取游戏信息并检查是否需要推送
    msg_list = await get_epic_free()
    if not check_push(msg_list):
        logger.info("Epic 游戏信息未更新，无需推送。")
        return

    try:
        if sub_info["sub_type"] == "群聊":
            await bot.send_group_forward_msg(group_id=int(sub_info["subject"]), messages=msg_list)
        else:  # 私聊
            await bot.send_private_forward_msg(user_id=int(sub_info["subject"]), messages=msg_list)
        logger.info(f"Epic 推送任务 {job_id} 执行成功。")
    except Exception as e:
        logger.error(f"Epic 推送任务 {job_id} 失败: {e.__class__.__name__}\n{format_exc()}")


# -------------------- 机器人启动时加载任务 --------------------
@get_driver().on_startup
async def load_epic_jobs():
    """启动时从文件中加载所有已保存的定时任务"""
    logger.info("正在从文件加载 Epic 推送任务...")
    sched_file = get_plugin_data_file("scheduler.json")
    if not sched_file.exists():
        logger.info("未找到 Epic 任务配置文件，跳过加载。")
        return

    import json
    sched_data: Dict[str, str] = json.loads(sched_file.read_text(encoding="UTF-8"))
    job_count = 0
    for job_id, cron_time in sched_data.items():
        try:
            _, sub_type, subject_id = job_id.split("_", 2)
            sub_type_cn = "群聊" if sub_type == "group" else "私聊"
            sub_info = {"sub_type": sub_type_cn, "subject": subject_id}

            minute, hour = cron_time.split()

            scheduler.add_job(
                push_epic_free, "cron", hour=hour, minute=minute, id=job_id, replace_existing=True,
                kwargs={"job_id": job_id, "sub_info": sub_info}
            )
            job_count += 1
        except Exception:
            logger.error(f"加载 Epic 任务 {job_id} 失败，配置可能已损坏。\n{format_exc()}")

    logger.info(f"成功加载 {job_count} 个 Epic 推送任务。")
