import os
from nonebot.log import logger
from .config import ScopedConfig

def init_proxy(plugin_config : ScopedConfig):
    """初始化代理设置，根据配置文件设置全局代理环境变量。"""
    print("test = ")
    print(plugin_config)
    if plugin_config.proxy_type:
        _proxy_url_base = ""
        if plugin_config.proxy_type.lower() == "socks5":
            _proxy_url_base = f"socks5://{plugin_config.proxy_host}:{plugin_config.proxy_port}"
        elif plugin_config.proxy_type.lower() == "http":
            _proxy_url_base = f"http://{plugin_config.proxy_host}:{plugin_config.proxy_port}"

        if plugin_config.proxy_username and plugin_config.proxy_password:
            # 如果有用户名和密码，格式化 URL
            _auth_part = f"{plugin_config.proxy_username}:{plugin_config.proxy_password}@"
            # 将 "socks5://" 或 "http://" 替换为包含认证信息的新格式
            _proxy_url_base = _proxy_url_base.replace("://", f"://_auth_part")

        if _proxy_url_base:
            # 为 httpx 设置全局代理环境变量
            # 注意：httpx 同时识别小写和大写变量，但小写优先级更高。为保险起见，我们都设置。
            proxy_env_vars = {
                "HTTP_PROXY": _proxy_url_base,
                "HTTPS_PROXY": _proxy_url_base,
                "ALL_PROXY": _proxy_url_base,
                "http_proxy": _proxy_url_base,
                "httpss_proxy": _proxy_url_base,
                "all_proxy": _proxy_url_base,
            }
            logger.success(f"[Proxy Config] 已启用全局代理: {_proxy_url_base}")
            os.environ.update(proxy_env_vars)
        else:
            logger.warning(f"[Proxy Config] 无效的 proxy_type: {plugin_config.proxy_type}")
    else:
        logger.info("[Proxy Config] 未配置代理, 将直接连接。")
