# -*- coding: utf-8 -*-
"""
logging 子包初始化

导出日志工具函数供外部直接引用。
"""

from aid_sdk.logging.aid_logger import get_logger, log_api_call

__all__ = ['get_logger', 'log_api_call']
