<div align="center">
    <a href="https://v2.nonebot.dev/store">
    <img src="https://raw.githubusercontent.com/fllesser/nonebot-plugin-template/refs/heads/resource/.docs/NoneBotPlugin.svg" width="310" alt="logo"></a>

## ✨ Epic喜加一 ✨

[![LICENSE](https://img.shields.io/github/license/FlanChanXwO/nonebot-plugin-epicfree.svg)](./LICENSE)
[![pypi](https://img.shields.io/pypi/v/nonebot-plugin-epicfree.svg)](https://pypi.python.org/pypi/nonebot-plugin-epicfree)
[![python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)
[![NoneBot](https://img.shields.io/badge/NoneBot-2.2.0+-green.svg)](https://github.com/nonebot/nonebot2)

</div>

## 📖 介绍

一个用于订阅和推送 Epic Games Store 每周免费游戏的 NoneBot2 插件。

功能特色：

- **定时推送**：每天定时检查并推送最新的喜加一游戏信息。
- **指令查询**：随时使用指令查询本周和下周的免费游戏。
- **灵活订阅**：支持群聊和私聊分别订阅，推送时间可自定义。
- **代理支持**：内置完善的代理配置，方便在网络受限的环境下使用。
- **权限管理**：订阅、取消订阅等指令可配置为仅限管理员/群主使用。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装 (推荐)</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-epicfree

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-epicfree

</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-epicfree

</details>
<details>
<summary>uv</summary>

    uv pip install nonebot-plugin-epicfree

</details>

然后打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_epicfree"]

</details>

## ⚙️ 配置

在 nonebot2 项目的 `.env` 或 `.env.prod` 文件中添加下表中的配置。

### 代理配置 (可选)

如果您的服务器无法直接访问 Epic Games API (例如，在中国大陆)，则需要配置代理。

|          配置项           | 必填 |     默认值     | 说明                                                                                         |
|:----------------------:|:--:|:-----------:|:-------------------------------------------------------------------------------------------|
|   `EPIC__PROXY_TYPE`   | 否  |     (无)     | 代理类型，可选 "http" 或 "socks5"。留空或不填则不使用代理。                                                     |
|   `EPIC__PROXY_HOST`   | 否  | `127.0.0.1` | 代理服务器的地址。                                                                                  |
|   `EPIC__PROXY_PORT`   | 否  |   `7890`    | 代理服务器的端口。                                                                                  |
| `EPIC__PROXY_USERNAME` | 否  |     (无)     | 代理的用户名 (如果需要认证)。                                                                           |
| `EPIC__PROXY_PASSWORD` | 否  |     (无)     | 代理的密码 (如果需要认证)。                                                                            |
| `EPIC__SUPERUSER_ONLY` | 否  |    `False`    | 是否仅允许超级用户 (SUPERUSERS) 执行订阅/取消订阅操作。设置为 `True`后，群管理和普通用户将无法使用订阅相关指令。                        |


**代理配置示例:**

```env
# 使用本地 7890 端口的 http 代理
EPIC__PROXY_TYPE="http"
EPIC__PROXY_HOST="127.0.0.1"
EPIC__PROXY_PORT=7890
```

## 🎉 使用

### 指令表

|    指令 (别名)    |    权限     | 说明                                                      |
|:-------------:|:---------:|:--------------------------------------------------------|
| `epic` (喜加一)  |   所有用户    | 获取本周和下周的 Epic 免费游戏信息。                                   |
| `epic订阅 <时间>` | 群管/群主/超管* | 在当前群聊或私聊中订阅每日定时推送。时间格式为 `时:分` (24小时制)，例如 `epic订阅 8:30`。 |
|  `epic取消订阅`   | 群管/群主/超管* | 在当前群聊或私聊中取消订阅。                                          |
|  `epic订阅状态`   |   所有用户    | 查看当前群聊或私聊的订阅状态和推送时间。                                    |
|   `epic刷新`    |   超级用户    | 强制刷新 Epic 免费游戏信息缓存。                                     |


### 🎨 效果图

**查询效果:**

![img_3.png](https://github.com/FlanChanXwO/nonebot-plugin-epicfree/blob/main/assets/img_3.png)

**订阅与推送效果:**
 
![img_1.png](https://github.com/FlanChanXwO/nonebot-plugin-epicfree/blob/main/assets/img_1.png)

![img_2.png](https://github.com/FlanChanXwO/nonebot-plugin-epicfree/blob/main/assets/img_2.png)

-----------------
## ️🙏 致谢
**特别鸣谢**

[@nonebot/nonebot2](https://github.com/nonebot/nonebot2/) | [@Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp) | [@DIYgod/RSSHub](https://github.com/DIYgod/RSSHub) | [@SD4RK/epicstore_api](https://github.com/SD4RK/epicstore_api)