# -*- coding: utf-8 -*-
"""
异常定义模块

定义 AID Client SDK 的自定义异常类。
"""

from typing import Optional, Union


class AidException(Exception):
    """AID SDK 自定义异常类。

    统一处理 SDK 中发生的业务异常，包含错误码和中文错误描述。

    Attributes:
        error_code: 数字错误码
        error_message: 中文错误描述
    """

    def __init__(
        self,
        error_code_or_enum: Union[int, 'ErrorCode'],  # type: ignore[name-defined]
        error_message: Optional[str] = None,
    ) -> None:
        """初始化异常对象。

        Args:
            error_code_or_enum: 可传入 ErrorCode 枚举值，或直接传入数字错误码
            error_message: 错误描述（当 error_code_or_enum 为数字时必填）
        """
        # 延迟导入避免循环引用
        from aid_sdk.common.error_codes import ErrorCode

        if isinstance(error_code_or_enum, ErrorCode):
            self.error_code: int = error_code_or_enum.code
            self.error_message: str = error_code_or_enum.message
        else:
            self.error_code = int(error_code_or_enum)
            self.error_message = error_message or "未知错误"

        super().__init__(f"[{self.error_code}] {self.error_message}")

    def __str__(self) -> str:
        return f"AidException(code={self.error_code}, message={self.error_message})"
