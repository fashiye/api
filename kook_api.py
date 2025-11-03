import requests
import json
import logging
from typing import Optional, Dict, Any, List, Callable

class ConfigManager:
    """配置管理器类，专门用于管理Kook API的配置"""
    
    def __init__(self, config: Dict):
        """
        初始化配置管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
    
    def get_bot_token(self) -> Optional[str]:
        """获取机器人token"""
        return self.config.get('kook', {}).get('bot_token')
    
    def get_channel_id(self) -> Optional[str]:
        """获取频道ID"""
        return self.config.get('kook', {}).get('channel_id')
    
    def get_server_id(self) -> Optional[str]:
        """获取服务器ID（从频道ID中提取）"""
        channel_id = self.get_channel_id()
        if channel_id:
            # 频道ID格式通常为服务器ID_频道ID，这里返回完整的频道ID
            # 如果需要服务器ID，可以从频道ID中解析
            return channel_id
        return None
    
    def get_message_template(self) -> str:
        """获取消息模板"""
        return self.config.get('kook', {}).get('message_template', "**[{player}]** {message}")
    
    def validate_config(self) -> Dict[str, bool]:
        """验证配置是否完整"""
        return {
            'bot_token': bool(self.get_bot_token()),
            'channel_id': bool(self.get_channel_id())
        }

class MessageSender:
    """消息发送器类，专门用于发送文字消息到Kook频道"""
    
    def __init__(self, api_instance):
        """
        初始化消息发送器
        
        Args:
            api_instance: KookAPI实例
        """
        self.api = api_instance
        self.logger = api_instance.logger
    
    def send_text(self, content: str, channel_id: Optional[str] = None) -> bool:
        """
        发送文字消息到Kook频道
        
        Args:
            content: 要发送的消息内容
            channel_id: 频道ID，如果为None则使用配置中的频道ID
            
        Returns:
            bool: 发送是否成功
        """
        try:
            if channel_id is None:
                channel_id = self.api.config_manager.get_channel_id()
            
            if not channel_id:
                self.logger.error("未提供频道ID")
                return False
            
            if not content or not content.strip():
                self.logger.warning("消息内容为空，跳过发送")
                return False
            
            url = f"{self.api.base_url}/message/create"
            payload = {
                "channel_id": channel_id,
                "content": content.strip(),
                "type": 1
            }
            
            response = requests.post(url, headers=self.api.headers, data=json.dumps(payload))
            response_data = response.json()
            
            if response_data.get('code') == 0:
                self.logger.info(f"消息发送成功到频道 {channel_id}: {content[:50]}...")
                return True
            else:
                error_msg = response_data.get('message', '未知错误')
                self.logger.error(f"发送消息失败: {error_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"发送消息时出错: {e}")
            return False
    
    def send_multiple(self, messages: List[str], channel_id: Optional[str] = None) -> Dict[str, bool]:
        """
        批量发送多条消息
        
        Args:
            messages: 消息内容列表
            channel_id: 频道ID，如果为None则使用配置中的频道ID
            
        Returns:
            Dict[str, bool]: 每条消息的发送结果，键为消息内容，值为是否成功
        """
        results = {}
        
        for i, message in enumerate(messages, 1):
            if not message or not message.strip():
                self.logger.warning(f"跳过第{i}条空消息")
                results[message] = False
                continue
                
            success = self.send_text(message, channel_id)
            results[message] = success
            
            # 添加短暂延迟避免API限制
            if i < len(messages):
                import time
                time.sleep(0.5)
             
        return results
    
    def send_formatted(self, title: str, content: str, channel_id: Optional[str] = None) -> bool:
        """
        发送格式化消息（标题+内容）
        
        Args:
            title: 消息标题
            content: 消息内容
            channel_id: 频道ID，如果为None则使用配置中的频道ID
            
        Returns:
            bool: 发送是否成功
        """
        formatted_message = f"**{title}**\n{content}"
        return self.send_text(formatted_message, channel_id)

class KookAPI:
    def __init__(self, plugin_instance, config):
        self.plugin_instance = plugin_instance
        self.config = config
        
        # 初始化配置管理器
        self.config_manager = ConfigManager(config)
        
        self.base_url = "https://www.kookapp.cn/api/v3"
        self.headers = {
            "Authorization": f"Bot {self.config_manager.get_bot_token() or ''}",
            "Content-Type": "application/json"
        }
        self.logger = plugin_instance.logger
        
        # 初始化消息发送器
        self.sender = MessageSender(self)

    # 配置管理相关方法
    def get_bot_token(self) -> Optional[str]:
        """获取机器人token"""
        return self.config_manager.get_bot_token()
    
    def get_channel_id(self) -> Optional[str]:
        """获取频道ID"""
        return self.config_manager.get_channel_id()
    
    def get_server_id(self) -> Optional[str]:
        """获取服务器ID"""
        return self.config_manager.get_server_id()
    
    def get_message_template(self) -> str:
        """获取消息模板"""
        return self.config_manager.get_message_template()
    
    def validate_config(self) -> Dict[str, bool]:
        """验证配置是否完整"""
        return self.config_manager.validate_config()
    
    def set_bot_token(self, token: str) -> bool:
        """设置机器人token"""
        try:
            self.config_manager.config['kook']['bot_token'] = token
            # 更新headers中的Authorization
            self.headers["Authorization"] = f"Bot {token}"
            return True
        except Exception as e:
            self.logger.error(f"设置机器人token失败: {e}")
            return False
    
    def set_channel_id(self, channel_id: str) -> bool:
        """设置频道ID"""
        try:
            self.config_manager.config['kook']['channel_id'] = channel_id
            return True
        except Exception as e:
            self.logger.error(f"设置频道ID失败: {e}")
            return False

    def send_message(self, content: str, channel_id: Optional[str] = None) -> bool:
        """Send message to Kook channel (兼容旧版本)"""
        return self.sender.send_text(content, channel_id)
    
    def send_card_message(self, card: Dict[str, Any], channel_id: Optional[str] = None) -> bool:
        """Send card message to Kook channel"""
        try:
            if channel_id is None:
                channel_id = self.config_manager.get_channel_id()
            
            if not channel_id:
                self.logger.error("No channel ID provided")
                return False
            
            url = f"{self.base_url}/message/create"
            payload = {
                "channel_id": channel_id,
                "type": 10,
                "content": json.dumps(card)
            }
            
            response = requests.post(url, headers=self.headers, data=json.dumps(payload))
            response_data = response.json()
            
            if response_data.get('code') == 0:
                self.logger.debug(f"Card message sent successfully to channel {channel_id}")
                return True
            else:
                self.logger.error(f"Failed to send card message: {response_data.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending card message to Kook: {e}")
            return False
    
    def get_channel_info(self, channel_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get channel information"""
        try:
            if channel_id is None:
                channel_id = self.config_manager.get_channel_id()
            
            if not channel_id:
                self.logger.error("No channel ID provided")
                return None
            
            url = f"{self.base_url}/channel/view?channel_id={channel_id}"
            response = requests.get(url, headers=self.headers)
            response_data = response.json()
            
            if response_data.get('code') == 0:
                return response_data.get('data')
            else:
                self.logger.error(f"Failed to get channel info: {response_data.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting channel info: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test connection to Kook API"""
        try:
            url = f"{self.base_url}/user/me"
            response = requests.get(url, headers=self.headers)
            response_data = response.json()
            
            if response_data.get('code') == 0:
                self.logger.info("Successfully connected to Kook API")
                return True
            else:
                self.logger.error(f"Failed to connect to Kook API: {response_data.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    def get_last_message(self, channel_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取指定频道的最后一条消息
        
        Args:
            channel_id: 频道ID，如果为None则使用配置中的频道ID
            
        Returns:
            Dict[str, Any]: 最后一条消息的数据，如果获取失败则返回None
        """
        try:
            if channel_id is None:
                channel_id = self.config_manager.get_channel_id()
            
            if not channel_id:
                self.logger.error("No channel ID provided")
                return None
            
            # 使用消息列表接口，限制返回1条消息
            url = f"{self.base_url}/message/list"
            params = {
                "channel_id": channel_id,
                "page_size": 1,  # 只获取1条消息
                "sort": "-created_at"  # 按创建时间倒序排列
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response_data = response.json()
            
            if response_data.get('code') == 0:
                messages = response_data.get('data', {}).get('items', [])
                if messages:
                    last_message = messages[0]
                    self.logger.info(f"成功获取最后一条消息: {last_message.get('content', '')[:50]}...")
                    return last_message
                else:
                    self.logger.info("频道中没有消息")
                    return None
            else:
                self.logger.error(f"获取消息失败: {response_data.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取最后一条消息时出错: {e}")
            return None

    def get_last_message_content(self, channel_id: Optional[str] = None) -> Optional[str]:
        """获取指定频道最后一条消息的内容
        
        Args:
            channel_id: 频道ID，如果为None则使用配置中的频道ID
            
        Returns:
            str: 最后一条消息的内容，如果获取失败则返回None
        """
        try:
            last_message = self.get_last_message(channel_id)
            if last_message:
                content = last_message.get('content', '')
                self.logger.info(f"最后一条消息内容: {content}")
                return content
            else:
                self.logger.info("没有获取到消息内容")
                return None
                
        except Exception as e:
            self.logger.error(f"获取消息内容时出错: {e}")
            return None

    def get_last_message_with_author(self, channel_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取最后一条消息及其作者信息
        
        Args:
            channel_id: 频道ID，如果为None则使用配置中的频道ID
            
        Returns:
            Dict[str, Any]: 包含消息内容和作者信息的字典，格式为:
            {
                'content': '消息内容',
                'author': {
                    'username': '用户名',
                    'nickname': '昵称',
                    'id': '用户ID'
                },
                'timestamp': '消息时间戳'
            }
        """
        try:
            last_message = self.get_last_message(channel_id)
            if not last_message:
                return None
            
            # 提取消息信息
            result = {
                'content': last_message.get('content', ''),
                'author': {
                    'username': last_message.get('author', {}).get('username', ''),
                    'nickname': last_message.get('author', {}).get('nickname', ''),
                    'id': last_message.get('author', {}).get('id', '')
                },
                'timestamp': last_message.get('create_at', 0),
                'message_id': last_message.get('id', ''),
                'channel_id': last_message.get('channel_id', '')
            }
            
            self.logger.info(f"获取到完整消息信息: {result['author'].get('nickname') or result['author'].get('username')}: {result['content'][:30]}...")
            return result
            
        except Exception as e:
            self.logger.error(f"获取消息和作者信息时出错: {e}")
            return None

    def get_last_n_messages(self, n: int = 5, channel_id: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """获取指定频道的最后N条消息
        
        Args:
            n: 要获取的消息数量，最大100
            channel_id: 频道ID，如果为None则使用配置中的频道ID
            
        Returns:
            List[Dict[str, Any]]: 消息列表，如果获取失败则返回None
        """
        try:
            if channel_id is None:
                channel_id = self.config_manager.get_channel_id()
            
            if not channel_id:
                self.logger.error("No channel ID provided")
                return None
            
            # 限制最大获取数量
            if n > 100:
                n = 100
                self.logger.warning("消息数量超过100，自动限制为100条")
            
            url = f"{self.base_url}/message/list"
            params = {
                "channel_id": channel_id,
                "page_size": n,
                "sort": "-created_at"  # 按创建时间倒序排列
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response_data = response.json()
            
            if response_data.get('code') == 0:
                messages = response_data.get('data', {}).get('items', [])
                self.logger.info(f"成功获取 {len(messages)} 条消息")
                return messages
            else:
                self.logger.error(f"获取消息列表失败: {response_data.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            self.logger.error(f"获取消息列表时出错: {e}")
            return None




class CommandHandler:
    """Kook机器人命令处理器类，用于注册和管理命令"""
    
    def __init__(self, kook_api: KookAPI, command_prefix: str = "!", logger=None):
        """
        初始化命令处理器
        
        Args:
            kook_api: KookAPI实例
            command_prefix: 命令前缀，默认为"!"
            logger: 日志记录器
        """
        self.kook_api = kook_api
        self.command_prefix = command_prefix
        self.logger = logger or kook_api.logger
        self.commands = {}  # 存储注册的命令
        self.aliases = {}   # 存储命令别名
        self.permissions = {}  # 存储命令权限
        
        # 注册内置命令
        self._register_builtin_commands()
    
    def _register_builtin_commands(self):
        """注册内置命令"""
        # 帮助命令
        self.register_command(
            name="help",
            func=self._help_command,
            description="显示帮助信息",
            usage="[命令名]",
            aliases=["h", "帮助"]
        )
        
        # 状态命令
        self.register_command(
            name="status",
            func=self._status_command,
            description="显示机器人状态",
            aliases=["状态", "stat"]
        )
        
        # 测试命令
        self.register_command(
            name="test",
            func=self._test_command,
            description="测试机器人连接",
            aliases=["测试"]
        )
    
    def register_command(self, name: str, func: Callable, description: str = "", 
                        usage: str = "", aliases: List[str] = None, 
                        permission_level: int = 0) -> bool:
        """
        注册命令
        
        Args:
            name: 命令名称
            func: 命令处理函数
            description: 命令描述
            usage: 命令用法
            aliases: 命令别名列表
            permission_level: 权限级别 (0=所有用户, 1=管理员, 2=超级管理员)
            
        Returns:
            bool: 注册是否成功
        """
        try:
            if name in self.commands:
                self.logger.warning(f"命令 '{name}' 已存在，将被覆盖")
            
            # 注册主命令
            self.commands[name] = {
                'func': func,
                'description': description,
                'usage': usage,
                'permission_level': permission_level
            }
            
            # 注册权限
            self.permissions[name] = permission_level
            
            # 注册别名
            if aliases:
                for alias in aliases:
                    if alias in self.aliases:
                        self.logger.warning(f"别名 '{alias}' 已存在，将被覆盖")
                    self.aliases[alias] = name
            
            self.logger.info(f"命令 '{name}' 注册成功 (权限级别: {permission_level})")
            return True
            
        except Exception as e:
            self.logger.error(f"注册命令 '{name}' 失败: {e}")
            return False
    
    def unregister_command(self, name: str) -> bool:
        """
        注销命令
        
        Args:
            name: 命令名称
            
        Returns:
            bool: 注销是否成功
        """
        try:
            if name not in self.commands:
                self.logger.warning(f"命令 '{name}' 不存在")
                return False
            
            # 删除主命令
            del self.commands[name]
            del self.permissions[name]
            
            # 删除相关别名
            aliases_to_remove = [alias for alias, cmd_name in self.aliases.items() if cmd_name == name]
            for alias in aliases_to_remove:
                del self.aliases[alias]
            
            self.logger.info(f"命令 '{name}' 注销成功")
            return True
            
        except Exception as e:
            self.logger.error(f"注销命令 '{name}' 失败: {e}")
            return False
    
    def parse_command(self, message: str) -> Dict[str, Any]:
        """
        解析命令消息
        
        Args:
            message: 原始消息内容
            
        Returns:
            Dict[str, Any]: 解析结果，包含命令名、参数等信息
        """
        if not message.startswith(self.command_prefix):
            return {'is_command': False}
        
        # 移除命令前缀
        content = message[len(self.command_prefix):].strip()
        
        if not content:
            return {'is_command': False}
        
        # 分割命令和参数
        parts = content.split()
        command_name = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # 检查是否是别名
        actual_command = self.aliases.get(command_name, command_name)
        
        if actual_command not in self.commands:
            return {
                'is_command': True,
                'valid': False,
                'command_name': command_name,
                'error': f"未知命令: {command_name}"
            }
        
        return {
            'is_command': True,
            'valid': True,
            'command_name': actual_command,
            'original_name': command_name,
            'args': args,
            'raw_args': ' '.join(args)
        }
    
    def execute_command(self, command_info: Dict[str, Any], user_info: Dict[str, Any] = None) -> str:
        """
        执行命令
        
        Args:
            command_info: 解析后的命令信息
            user_info: 用户信息，用于权限检查
            
        Returns:
            str: 命令执行结果
        """
        if not command_info.get('valid', False):
            return command_info.get('error', '命令无效')
        
        command_name = command_info['command_name']
        
        # 检查权限
        if not self._check_permission(command_name, user_info):
            return "权限不足，无法执行此命令"
        
        try:
            # 获取命令函数
            command_data = self.commands[command_name]
            func = command_data['func']
            
            # 执行命令
            result = func(command_info['args'], command_info['raw_args'])
            
            self.logger.info(f"命令 '{command_name}' 执行成功")
            return result
            
        except Exception as e:
            error_msg = f"执行命令 '{command_name}' 时出错: {e}"
            self.logger.error(error_msg)
            return error_msg
    
    def _check_permission(self, command_name: str, user_info: Dict[str, Any] = None) -> bool:
        """
        检查用户权限
        
        Args:
            command_name: 命令名称
            user_info: 用户信息
            
        Returns:
            bool: 是否有权限执行命令
        """
        if command_name not in self.permissions:
            return False
        
        required_level = self.permissions[command_name]
        
        # 权限级别说明:
        # 0: 所有用户
        # 1: 管理员 (需要user_info中包含is_admin=True)
        # 2: 超级管理员 (需要user_info中包含is_super_admin=True)
        
        if required_level == 0:
            return True
        
        if not user_info:
            return False
        
        if required_level == 1 and user_info.get('is_admin', False):
            return True
        
        if required_level == 2 and user_info.get('is_super_admin', False):
            return True
        
        return False
    
    def process_message(self, message: str, user_info: Dict[str, Any] = None) -> str:
        """
        处理消息，如果是命令则执行
        
        Args:
            message: 消息内容
            user_info: 用户信息
            
        Returns:
            str: 处理结果，如果不是命令则返回空字符串
        """
        command_info = self.parse_command(message)
        
        if not command_info['is_command']:
            return ""
        
        if not command_info['valid']:
            return command_info['error']
        
        return self.execute_command(command_info, user_info)
    
    def get_command_list(self) -> List[Dict[str, Any]]:
        """
        获取所有命令列表
        
        Returns:
            List[Dict[str, Any]]: 命令信息列表
        """
        commands = []
        for name, data in self.commands.items():
            commands.append({
                'name': name,
                'description': data['description'],
                'usage': data['usage'],
                'permission_level': data['permission_level'],
                'aliases': [alias for alias, cmd_name in self.aliases.items() if cmd_name == name]
            })
        return commands
    
    # 内置命令实现
    def _help_command(self, args: List[str], raw_args: str) -> str:
        """帮助命令"""
        if args:
            # 显示特定命令的帮助
            command_name = args[0].lower()
            actual_command = self.aliases.get(command_name, command_name)
            
            if actual_command in self.commands:
                command_data = self.commands[actual_command]
                help_text = f"**命令: {actual_command}**\n"
                help_text += f"描述: {command_data['description']}\n"
                
                if command_data['usage']:
                    help_text += f"用法: {self.command_prefix}{actual_command} {command_data['usage']}\n"
                else:
                    help_text += f"用法: {self.command_prefix}{actual_command}\n"
                
                aliases = [alias for alias, cmd_name in self.aliases.items() if cmd_name == actual_command]
                if aliases:
                    help_text += f"别名: {', '.join(aliases)}\n"
                
                help_text += f"权限级别: {command_data['permission_level']}"
                return help_text
            else:
                return f"未知命令: {command_name}"
        else:
            # 显示所有命令列表
            commands = self.get_command_list()
            help_text = "**可用命令列表:**\n"
            
            for cmd in commands:
                if cmd['permission_level'] == 0:  # 只显示普通用户可用的命令
                    help_text += f"• {self.command_prefix}{cmd['name']}"
                    if cmd['aliases']:
                        help_text += f" ({', '.join(cmd['aliases'])})"
                    help_text += f" - {cmd['description']}\n"
            
            help_text += f"\n使用 {self.command_prefix}help [命令名] 查看详细帮助"
            return help_text
    
    def _status_command(self, args: List[str], raw_args: str) -> str:
        """状态命令"""
        status_text = "**机器人状态信息**\n"
        status_text += f"• 命令前缀: {self.command_prefix}\n"
        status_text += f"• 已注册命令: {len(self.commands)} 个\n"
        status_text += f"• 命令别名: {len(self.aliases)} 个\n"
        
        # 测试API连接
        if self.kook_api.test_connection():
            status_text += "• API连接: ✅ 正常\n"
        else:
            status_text += "• API连接: ❌ 异常\n"
        
        # 检查配置
        config_status = self.kook_api.validate_config()
        for key, valid in config_status.items():
            status_text += f"• {key}: {'✅' if valid else '❌'}\n"
        
        return status_text
    
    def _test_command(self, args: List[str], raw_args: str) -> str:
        """测试命令"""
        if self.kook_api.test_connection():
            return "✅ 机器人连接正常"
        else:
            return "❌ 机器人连接异常，请检查配置"
    
    def set_command_prefix(self, prefix: str) -> bool:
        """
        设置命令前缀
        
        Args:
            prefix: 新的命令前缀
            
        Returns:
            bool: 设置是否成功
        """
        if not prefix or len(prefix) > 3:
            self.logger.error("命令前缀不能为空且长度不能超过3个字符")
            return False
        
        self.command_prefix = prefix
        self.logger.info(f"命令前缀已设置为: '{prefix}'")
        return True
    
    def get_command_info(self, command_name: str) -> Optional[Dict[str, Any]]:
        """
        获取命令详细信息
        
        Args:
            command_name: 命令名称
            
        Returns:
            Optional[Dict[str, Any]]: 命令信息，如果不存在则返回None
        """
        actual_command = self.aliases.get(command_name, command_name)
        
        if actual_command not in self.commands:
            return None
        
        command_data = self.commands[actual_command]
        return {
            'name': actual_command,
            'description': command_data['description'],
            'usage': command_data['usage'],
            'permission_level': command_data['permission_level'],
            'aliases': [alias for alias, cmd_name in self.aliases.items() if cmd_name == actual_command]
        }
