import json
from typing import Dict, Literal, Optional, Union
from nonebot import require

require("nonebot_plugin_localstore")
from nonebot_plugin_localstore import get_plugin_data_file

try:
    from nonebot.adapters.onebot.v11 import Message, MessageSegment  # type: ignore
except ImportError:
    from nonebot.adapters.cqhttp import Message, MessageSegment  # type: ignore

# 任务调度配置文件
scheduler_file = get_plugin_data_file("scheduler.json")

async def scheduler_manage(
    job_id: str,
    action: Literal["get", "set", "delete"] = "get",
    time: Optional[str] = None,
) -> Optional[Union[str, Dict[str, str]]]:  # <-- 修改这里
    """
    管理定时任务配置 (cron 表达式)
    action 'get' -> returns str | None
    action 'set' -> returns Dict | None
    action 'delete' -> returns None
    """
    if scheduler_file.exists():
        sched_data: Dict[str, str] = json.loads(
            scheduler_file.read_text(encoding="UTF-8")
        )
    else:
        sched_data = {}

    if action == "get":
        return sched_data.get(job_id)  # 返回 str 或 None

    elif action == "set":
        if not time:
            raise ValueError("设置定时任务时必须提供时间参数 'time'!")
        sched_data[job_id] = time

    elif action == "delete":
        sched_data.pop(job_id, None)

    # 写回文件
    scheduler_file.write_text(
        json.dumps(sched_data, ensure_ascii=False, indent=2), encoding="UTF-8"
    )
    # 如果是set, 返回设置后的值
    if action == "set":
        return {"job_id": job_id, "time": time} # 返回 Dict
    return None