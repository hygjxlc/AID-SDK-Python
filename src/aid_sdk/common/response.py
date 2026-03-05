# -*- coding: utf-8 -*-
"""
统一响应对象模块

定义 AID Client SDK 的标准响应数据结构。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class AidResponse:
    """AID SDK 统一响应数据类。

    Attributes:
        code: 响应状态码，200 表示成功
        message: 响应描述信息
        data: 响应数据，可为任意类型
    """

    code: int
    message: str
    data: Optional[Any] = field(default=None)

    @property
    def success(self) -> bool:
        """判断操作是否成功。

        Returns:
            当 code == 200 时返回 True，否则返回 False
        """
        return self.code == 200

    @classmethod
    def success_response(cls, data: Optional[Any] = None, message: str = "操作成功") -> 'AidResponse':
        """创建成功响应对象。

        Args:
            data: 响应数据
            message: 成功描述信息，默认为"操作成功"

        Returns:
            成功的 AidResponse 实例
        """
        return cls(code=200, message=message, data=data)

    @classmethod
    def failure_response(cls, code: int, message: str) -> 'AidResponse':
        """创建失败响应对象。

        Args:
            code: 错误码
            message: 错误描述信息

        Returns:
            失败的 AidResponse 实例
        """
        return cls(code=code, message=message, data=None)

    def to_dict(self) -> Dict[str, Any]:
        """将响应对象序列化为字典。

        Returns:
            包含 code、message、data 的字典
        """
        result: Dict[str, Any] = {
            'code': self.code,
            'message': self.message,
            'data': None,
        }
        # 如果 data 本身有 to_dict 方法则递归转换
        if self.data is not None:
            if hasattr(self.data, 'to_dict'):
                result['data'] = self.data.to_dict()
            else:
                result['data'] = self.data
        return result
