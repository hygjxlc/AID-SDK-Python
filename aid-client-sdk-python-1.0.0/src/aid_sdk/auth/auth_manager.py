# -*- coding: utf-8 -*-
"""
API Key 鉴权管理器

实现基于 API Key 的鉴权逻辑，从配置文件中读取 api_token。
"""

from aid_sdk.auth.auth_service import AuthService
from aid_sdk.config.config_manager import ConfigManager


class ApiKeyAuthManager(AuthService):
    """基于 API Key 的鉴权管理器。

    从 ConfigManager 中读取 api_token，并提供验证方法。

    Attributes:
        _config: 配置管理器实例
    """

    def __init__(self, config: ConfigManager) -> None:
        """初始化鉴权管理器。

        Args:
            config: 已加载的 ConfigManager 实例
        """
        self._config: ConfigManager = config

    def get_auth_token(self) -> str:
        """从配置中获取 API Token。

        Returns:
            配置文件中的 api_token 值
        """
        return self._config.get_api_token()

    def authenticate(self, token: str) -> bool:
        """验证传入的 Token 是否与配置中的 Token 一致。

        Args:
            token: 待验证的 Token 字符串

        Returns:
            Token 一致时返回 True，否则返回 False
        """
        configured_token = self._config.get_api_token()
        return token == configured_token

    def get_auth_type(self) -> str:
        """返回鉴权类型名称。

        Returns:
            固定返回 'api_key'
        """
        return "api_key"
