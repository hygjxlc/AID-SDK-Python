# -*- coding: utf-8 -*-
"""
鉴权服务抽象基类

定义鉴权服务的接口规范，所有鉴权实现均需继承此类。
"""

from abc import ABC, abstractmethod


class AuthService(ABC):
    """鉴权服务抽象基类。

    定义了获取 Token、验证 Token 和返回鉴权类型的标准接口。
    """

    @abstractmethod
    def get_auth_token(self) -> str:
        """获取当前有效的鉴权 Token。

        Returns:
            鉴权 Token 字符串
        """
        ...

    @abstractmethod
    def authenticate(self, token: str) -> bool:
        """验证给定的 Token 是否合法。

        Args:
            token: 待验证的 Token 字符串

        Returns:
            合法时返回 True，否则返回 False
        """
        ...

    @abstractmethod
    def get_auth_type(self) -> str:
        """返回当前鉴权类型名称。

        Returns:
            鉴权类型字符串，如 'api_key'
        """
        ...
