import os
from typing import Optional, Dict

from nonebot.log import logger
from .config import ScopedConfig


def get_proxy_url(plugin_config: ScopedConfig) -> Optional[str]:
    """
    根据插件配置生成 httpx 所需的代理 URL 字符串。
    如果不配置代理，则返回 None。
    """
    # 检查是否配置了代理类型和主机
    if not plugin_config.proxy_type or not plugin_config.proxy_host:
        logger.info("[Proxy Config] 未配置代理, 将直接连接。")
        return None

    proxy_url = ""
    proxy_type_lower = plugin_config.proxy_type.lower()

    # 仅支持 http 和 socks5
    if proxy_type_lower in ["socks5", "http"]:
        scheme = proxy_type_lower
        host_port = f"{plugin_config.proxy_host}:{plugin_config.proxy_port}"

        # 检查是否有认证信息
        if plugin_config.proxy_username and plugin_config.proxy_password:
            auth_part = f"{plugin_config.proxy_username}:{plugin_config.proxy_password}@"
            proxy_url = f"{scheme}://{auth_part}{host_port}"
        else:
            proxy_url = f"{scheme}://{host_port}"

    # 如果 proxy_url 仍然是空的，说明 proxy_type 无效
    if not proxy_url:
        logger.warning(f"[Proxy Config] 无效的 proxy_type: {plugin_config.proxy_type}")
        return None

    logger.success(f"[Proxy Config] 插件已配置代理: {proxy_url}")
    return proxy_url


