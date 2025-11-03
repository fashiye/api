# Kook API 模块文档

## 概述

`kook_api.py` 是 Kook 聊天桥接插件的核心模块，提供了与 Kook 平台 API 交互的功能。该模块包含三个主要类：`KookAPI`、`MessageSender` 和 `CommandHandler`，分别负责 API 连接管理、消息发送和命令处理功能。

## 文件结构

```
kook_chat_bridge/
├── kook_api.py          # 主要 API 模块
├── config.py            # 配置管理
├── message_formatter.py # 消息格式化
```

## 依赖项

- `requests` - HTTP 请求库
- `json` - JSON 数据处理
- `typing` - 类型注解支持


## 类文档

### ConfigManager 类

专门用于管理Kook API配置的配置管理器类。

#### 构造函数
```python
def __init__(self, config: Dict)
```
- `config`: 配置字典

#### 方法

##### get_bot_token()
获取机器人token。
- **返回**: `Optional[str]` - 机器人token，如果未设置则返回None

##### get_channel_id()
获取频道ID。
- **返回**: `Optional[str]` - 频道ID，如果未设置则返回None

##### get_server_id()
获取服务器ID（从频道ID中提取）。
- **返回**: `Optional[str]` - 服务器ID，如果未设置则返回None

##### get_message_template()
获取消息模板。
- **返回**: `str` - 消息模板字符串

##### validate_config()
验证配置是否完整。
- **返回**: `Dict[str, bool]` - 配置验证结果字典

### MessageSender 类

专门用于发送文字消息到 Kook 频道的消息发送器类。

#### 构造函数

```python
def __init__(self, api_instance)
```

**参数:**
- `api_instance` (KookAPI): KookAPI 实例

#### 方法

##### send_text

发送文字消息到 Kook 频道。

```python
def send_text(self, content: str, channel_id: Optional[str] = None) -> bool
```

**参数:**
- `content` (str): 要发送的消息内容
- `channel_id` (Optional[str]): 频道ID，如果为 None 则使用配置中的频道ID

**返回值:**
- `bool`: 发送是否成功

**示例:**
```python
success = sender.send_text("这是一条测试消息")
```

##### send_multiple

批量发送多条消息。

```python
def send_multiple(self, messages: List[str], channel_id: Optional[str] = None) -> Dict[str, bool]
```

**参数:**
- `messages` (List[str]): 消息内容列表
- `channel_id` (Optional[str]): 频道ID，如果为 None 则使用配置中的频道ID

**返回值:**
- `Dict[str, bool]`: 每条消息的发送结果，键为消息内容，值为是否成功

**示例:**
```python
messages = ["消息1", "消息2", "消息3"]
results = sender.send_multiple(messages)
```

##### send_formatted

发送格式化消息（标题+内容）。

```python
def send_formatted(self, title: str, content: str, channel_id: Optional[str] = None) -> bool
```

**参数:**
- `title` (str): 消息标题
- `content` (str): 消息内容
- `channel_id` (Optional[str]): 频道ID，如果为 None 则使用配置中的频道ID

**返回值:**
- `bool`: 发送是否成功

**示例:**
```python
success = sender.send_formatted("服务器状态", "服务器运行正常")
```

### KookAPI 类

主要的 Kook API 接口类，提供完整的 Kook 平台交互功能。

### CommandHandler 类

Kook 机器人命令处理器类，提供完整的命令注册、解析和执行功能。

#### 构造函数

```python
def __init__(self, config_manager, logger)
```

**参数:**
- `config_manager`: 配置管理器实例
- `logger`: 日志记录器实例

#### 核心功能

##### 命令注册

注册新的命令到处理器中。

```python
def register_command(self, command_name: str, callback: Callable, 
                   aliases: List[str] = None, permission_level: int = 0, 
                   description: str = "", usage: str = "") -> bool
```

**参数:**
- `command_name` (str): 主命令名称
- `callback` (Callable): 命令回调函数
- `aliases` (List[str]): 命令别名列表
- `permission_level` (int): 权限级别（0-普通用户，1-管理员，2-超级管理员）
- `description` (str): 命令描述
- `usage` (str): 命令使用说明

**返回值:**
- `bool`: 注册是否成功

**示例:**
```python
# 注册一个简单的问候命令
handler.register_command("greet", greet_callback, 
                       aliases=["hello", "hi"], 
                       description="发送问候消息",
                       usage="/greet [用户名]")
```

##### 命令解析和执行

解析用户输入的命令并执行相应的处理函数。

```python
def parse_and_execute(self, message: str, user_permission: int = 0) -> str
```

**参数:**
- `message` (str): 用户输入的消息
- `user_permission` (int): 用户权限级别

**返回值:**
- `str`: 命令执行结果或错误信息

**示例:**
```python
result = handler.parse_and_execute("/greet 小明", user_permission=0)
print(result)  # 输出: "你好，小明！"
```

##### 命令注销

从处理器中注销指定的命令。

```python
def unregister_command(self, command_name: str) -> bool
```

**参数:**
- `command_name` (str): 要注销的命令名称

**返回值:**
- `bool`: 注销是否成功

#### 内置命令

CommandHandler 类内置了以下实用命令：

##### help 命令
显示所有可用命令的帮助信息。
- **权限**: 0 (所有用户)
- **用法**: `/help [命令名]`

##### status 命令
显示命令处理器的状态信息。
- **权限**: 0 (所有用户)
- **用法**: `/status`

##### test 命令
测试命令处理器是否正常工作。
- **权限**: 0 (所有用户)
- **用法**: `/test`

#### 权限控制

支持多级权限控制，确保命令安全：
- **0级**: 普通用户权限
- **1级**: 管理员权限
- **2级**: 超级管理员权限

#### 错误处理

完善的错误处理机制：
- 命令不存在时的友好提示
- 权限不足的警告信息
- 参数解析错误的详细说明
- 命令执行异常的捕获和记录

### KookAPI 类

主要的 Kook API 接口类，提供完整的 Kook 平台交互功能。

#### 构造函数

```python
def __init__(self, plugin_instance, config)
```

**参数:**
- `plugin_instance`: MCDR 插件实例
- `config`: 配置字典

**属性:**
- `plugin_instance`: 插件实例
- `config`: 配置信息
- `base_url`: Kook API 基础 URL
- `headers`: HTTP 请求头
- `logger`: 日志记录器
- `sender`: MessageSender 实例

#### 配置管理方法

##### get_bot_token()
获取机器人token。
- **返回**: `Optional[str]` - 机器人token

##### get_channel_id()
获取频道ID。
- **返回**: `Optional[str]` - 频道ID

##### get_server_id()
获取服务器ID。
- **返回**: `Optional[str]` - 服务器ID

##### get_message_template()
获取消息模板。
- **返回**: `str` - 消息模板

##### validate_config()
验证配置是否完整。
- **返回**: `Dict[str, bool]` - 配置验证结果

##### set_bot_token(token)
设置机器人token。
- `token`: 新的机器人token
- **返回**: `bool` - 设置是否成功

##### set_channel_id(channel_id)
设置频道ID。
- `channel_id`: 新的频道ID
- **返回**: `bool` - 设置是否成功

#### 消息发送方法

##### send_message

发送消息到 Kook 频道（兼容旧版本）。

```python
def send_message(self, content: str, channel_id: Optional[str] = None) -> bool
```

**参数:**
- `content` (str): 消息内容
- `channel_id` (Optional[str]): 频道ID

**返回值:**
- `bool`: 发送是否成功

##### send_card_message

发送卡片消息到 Kook 频道。

```python
def send_card_message(self, card: Dict[str, Any], channel_id: Optional[str] = None) -> bool
```

**参数:**
- `card` (Dict[str, Any]): 卡片消息数据
- `channel_id` (Optional[str]): 频道ID

**返回值:**
- `bool`: 发送是否成功

#### 频道信息方法

##### get_channel_info

获取频道信息。

```python
def get_channel_info(self, channel_id: Optional[str] = None) -> Optional[Dict[str, Any]]
```

**参数:**
- `channel_id` (Optional[str]): 频道ID

**返回值:**
- `Optional[Dict[str, Any]]`: 频道信息字典

#### 连接测试方法

##### test_connection

测试与 Kook API 的连接。

```python
def test_connection(self) -> bool
```

**返回值:**
- `bool`: 连接是否成功

#### 消息获取方法

##### get_last_message

获取指定频道的最后一条消息。

```python
def get_last_message(self, channel_id: Optional[str] = None) -> Optional[Dict[str, Any]]
```

**参数:**
- `channel_id` (Optional[str]): 频道ID

**返回值:**
- `Optional[Dict[str, Any]]`: 最后一条消息的数据

##### get_last_message_content

获取指定频道最后一条消息的内容。

```python
def get_last_message_content(self, channel_id: Optional[str] = None) -> Optional[str]
```

**参数:**
- `channel_id` (Optional[str]): 频道ID

**返回值:**
- `Optional[str]`: 最后一条消息的内容

##### get_last_message_with_author

获取最后一条消息及其作者信息。

```python
def get_last_message_with_author(self, channel_id: Optional[str] = None) -> Optional[Dict[str, Any]]
```

**参数:**
- `channel_id` (Optional[str]): 频道ID

**返回值:**
- `Optional[Dict[str, Any]]`: 包含消息内容和作者信息的字典

**返回格式:**
```json
{
    "content": "消息内容",
    "author": {
        "username": "用户名",
        "nickname": "昵称", 
        "id": "用户ID"
    },
    "timestamp": "消息时间戳",
    "message_id": "消息ID",
    "channel_id": "频道ID"
}
```

##### get_last_n_messages

获取指定频道的最后 N 条消息。

```python
def get_last_n_messages(self, n: int = 5, channel_id: Optional[str] = None) -> Optional[List[Dict[str, Any]]]
```

**参数:**
- `n` (int): 要获取的消息数量，最大100
- `channel_id` (Optional[str]): 频道ID

**返回值:**
- `Optional[List[Dict[str, Any]]]`: 消息列表

## 配置要求

使用前需要在配置文件中设置 Kook 相关信息：

```json
{
    "kook": {
        "bot_token": "你的机器人token",
        "channel_id": "你的频道ID"
    }
}
```
### 基本使用

```python
from kook_chat_bridge.kook_api import KookAPI

# 创建 KookAPI 实例
kook_api = KookAPI(plugin_instance, config)

# 测试连接
if kook_api.test_connection():
    print("连接成功")

# 发送消息
kook_api.sender.send_text("这是一条测试消息")

# 获取最后一条消息
last_message = kook_api.get_last_message()
```

                                                                        ### 命令处理使用

```python
from kook_chat_bridge.kook_api import CommandHandler

# 创建命令处理器实例
command_handler = CommandHandler(config_manager, logger)

# 注册自定义命令
def greet_command(args):
    if args:
        return f"你好，{args[0]}！"
    else:
        return "你好！"

command_handler.register_command("greet", greet_command, 
                               aliases=["hello", "hi"], 
                               description="发送问候消息",
                               usage="/greet [用户名]")

# 处理用户命令
user_input = "/greet 小明"
result = command_handler.parse_and_execute(user_input, user_permission=0)
print(result)  # 输出: "你好，小明！"

# 显示帮助信息
help_result = command_handler.parse_and_execute("/help", user_permission=0)
print(help_result)
```

### 高级使用

```python
# 批量发送消息
messages = ["消息1", "消息2", "消息3"]
results = kook_api.sender.send_multiple(messages)

# 发送格式化消息
kook_api.sender.send_formatted("服务器公告", "服务器将于今晚维护")

# 获取消息详细信息
message_info = kook_api.get_last_message_with_author()
if message_info:
    print(f"作者: {message_info['author']['nickname']}")
    print(f"内容: {message_info['content']}")
```

## 错误处理

所有方法都包含完善的错误处理机制：

- 输入验证（空内容检查）
- 异常捕获和日志记录
- 详细的错误信息
- 合理的默认返回值

## 日志记录



- 成功操作日志
- 错误和警告信息
- 调试信息（可选）

## 兼容性说明

- 保持与旧版本 `send_message` 方法的兼容性
- 支持 Python 3.7+

## 注意事项

1. **API 限制**: 注意 Kook API 的调用频率限制
2. **配置安全**: 妥善保管 bot_token，避免泄露
3. **错误处理**: 所有网络操作都应包含错误处理
4. **日志监控**: 定期检查日志以发现潜在问题


## 版本历史

- v1.0: 初始版本，基础消息发送功能
- v1.1: 添加消息获取功能
- v1.2: 重构消息发送逻辑，新增 MessageSender 类
- v1.3: 新增 CommandHandler 类，提供完整的命令处理功能

---

*文档最后更新: 2025-11-03*
