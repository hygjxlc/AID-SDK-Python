# -*- coding: utf-8 -*-
"""
鉴权装饰器模块

提供 @require_auth 装饰器，自动将 api_key 注入被装饰函数的关键字参数中。
"""

import functools
from typing import Any, Callable

from aid_sdk.common.exceptions import AidException
from aid_sdk.common.error_codes import ErrorCode


def require_auth(auth_manager: Any) -> Callable:
    """创建一个注入 api_key 的装饰器。

    被装饰的函数需接受 api_key 关键字参数。装饰器会从 auth_manager
    中自动获取 Token 并注入。

    Args:
        auth_manager: 实现了 get_auth_token() 方法的鉴权管理器实例

    Returns:
        装饰器函数

    Example:
        @require_auth(auth_manager_instance)
        def my_func(data, api_key=None):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                token = auth_manager.get_auth_token()
            except Exception as exc:
                raise AidException(
                    ErrorCode.INTERNAL_ERROR.code,
                    f"获取鉴权 Token 失败：{exc}",
                ) from exc

            if not token:
                raise AidException(
                    ErrorCode.INTERNAL_ERROR.code,
                    "鉴权失败：api_token 为空，请检查配置文件",
                )

            # 将 api_key 注入函数关键字参数
            kwargs['api_key'] = token
            return func(*args, **kwargs)

        return wrapper
    return decorator
