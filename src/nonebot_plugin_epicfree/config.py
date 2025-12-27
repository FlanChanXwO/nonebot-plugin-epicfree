from pydantic import BaseModel, Field

class ScopedConfig(BaseModel):
    # 文档: https://www.python-httpx.org/advanced/#proxies
    # -------------------------------------------------------------------
    # --- 代理模式选择 ---
    # "http": 使用 HTTP 代理
    # "socks5": 使用 SOCKS5 代理
    # None (或注释掉): 不使用代理
    proxy_type: str | None = "http"  # 可选: "http", "socks5", None

    # --- 代理地址和端口 ---
    proxy_host: str = "127.0.0.1"  # 代理服务器地址
    proxy_port: int = 7890  # 代理服务器端口

    # --- 如果代理需要认证，请填写以下信息 ---
    proxy_username: str | None = None  # 代理用户名 (可选)
    proxy_password: str | None = None  # 代理密码 (可选)

    # -- 权限配置 --
    superuser_only: bool = False  # 是否仅允许超级用户使用 Epic Free 功能

class Config(BaseModel):
    """Epic Free Config 类"""
    epic: ScopedConfig = Field(default_factory=ScopedConfig)



