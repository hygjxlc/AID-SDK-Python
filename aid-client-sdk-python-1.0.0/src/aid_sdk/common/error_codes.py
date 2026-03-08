# -*- coding: utf-8 -*-
"""
错误码定义模块

定义 AID Client SDK 使用的所有错误码，采用枚举方式管理。
"""

from enum import Enum


class ErrorCode(Enum):
    """AID SDK 错误码枚举类。

    每个枚举值包含 (code, message) 元组，
    code 为数字错误码，message 为中文描述。
    """

    SUCCESS = (200, "操作成功")
    TASK_CREATE_FAILED = (301, "任务创建失败")
    FILE_VERIFY_FAILED = (302, "工作文件缺失/校验失败")
    FILE_UPLOAD_FAILED = (303, "上传文件失败")
    TASK_START_FAILED = (401, "任务开始失败")
    TASK_STOP_FAILED = (402, "任务停止失败")
    TASK_DELETE_FAILED = (403, "任务删除失败")
    RESULT_FETCH_FAILED = (404, "获取结果/状态失败")
    INTERNAL_ERROR = (500, "算法服务内部运行错误")

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message

    @classmethod
    def from_code(cls, code: int) -> 'ErrorCode':
        """根据数字错误码查找对应的枚举值。

        Args:
            code: 数字错误码

        Returns:
            对应的 ErrorCode 枚举值，找不到时返回 INTERNAL_ERROR
        """
        for member in cls:
            if member.code == code:
                return member
        return cls.INTERNAL_ERROR
