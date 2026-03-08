# -*- coding: utf-8 -*-
"""
CLI 工具基础模块

提供 CLI 命令公共辅助函数：JSON 输出格式化、错误打印和客户端创建。
"""

import json
import sys
from typing import Any

from aid_sdk.client import AidClient
from aid_sdk.common.exceptions import AidException


def print_json(data: Any) -> None:
    """将数据格式化为缩进 JSON 并输出到标准输出。

    Args:
        data: 可序列化为 JSON 的数据（字典、列表等）
    """
    print(json.dumps(data, ensure_ascii=False, indent=2))


def print_error(code: int, message: str) -> None:
    """将错误信息输出到标准错误流。

    Args:
        code: 错误码
        message: 错误描述信息
    """
    error_data = {'code': code, 'message': message, 'success': False}
    print(json.dumps(error_data, ensure_ascii=False, indent=2), file=sys.stderr)


def get_client(config_path: str = './config/config.yml') -> AidClient:
    """创建并返回 AidClient 实例。

    Args:
        config_path: 配置文件路径，默认为 './config/config.yml'

    Returns:
        初始化完成的 AidClient 实例

    Raises:
        SystemExit: 初始化失败时打印错误并退出
    """
    try:
        return AidClient(config_path)
    except AidException as exc:
        print_error(exc.error_code, exc.error_message)
        sys.exit(1)
    except Exception as exc:
        print_error(500, f"初始化客户端失败：{exc}")
        sys.exit(1)
