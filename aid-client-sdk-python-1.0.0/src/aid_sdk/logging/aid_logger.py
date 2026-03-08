# -*- coding: utf-8 -*-
"""
日志工具模块

提供 JSON 格式日志记录器，支持结构化字段（taskID、api、code）。
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

from pythonjsonlogger import jsonlogger

# 日志目录（相对于运行目录）
_LOG_DIR = "logs"
_LOG_FILE = os.path.join(_LOG_DIR, "aid-sdk.log")


def get_logger(name: str) -> logging.Logger:
    """创建并返回一个 JSON 格式的日志记录器。

    Args:
        name: 日志记录器名称（通常传入 __name__）

    Returns:
        配置好 JSON Handler（控制台 + 文件）的 Logger 实例
    """
    logger = logging.getLogger(name)

    # 避免重复添加 Handler
    if not logger.handlers:
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S',
        )

        # 控制台输出
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件输出（按天滚动，保留30天）
        os.makedirs(_LOG_DIR, exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            filename=_LOG_FILE,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8',
        )
        file_handler.suffix = "%Y-%m-%d"
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.setLevel(logging.DEBUG)

    return logger


def log_api_call(
    logger: logging.Logger,
    api: str,
    task_id: Optional[str] = None,
    message: str = "",
    level: str = 'info',
) -> None:
    """记录 API 调用的结构化日志。

    Args:
        logger: 日志记录器实例
        api: 调用的 API 名称
        task_id: 关联的任务 ID（可为 None）
        message: 日志消息内容
        level: 日志级别，支持 'info'、'warning'、'error'、'debug'
    """
    # 构造结构化日志附加字段
    extra = {
        'api': api,
        'taskID': task_id or '',
    }

    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message, extra=extra)
