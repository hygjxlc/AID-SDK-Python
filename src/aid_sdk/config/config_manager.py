# -*- coding: utf-8 -*-
"""
配置管理模块

负责读取和管理 YAML 格式的 SDK 配置文件。
"""

import os
from typing import Any, Dict, Optional

import yaml

from aid_sdk.common.exceptions import AidException
from aid_sdk.common.error_codes import ErrorCode


class ConfigManager:
    """YAML 配置文件管理器。

    负责从指定路径加载 YAML 配置文件，并提供键值查询接口。

    Attributes:
        _config_path: 配置文件路径
        _config: 内存中的配置字典
    """

    def __init__(self, config_path: str) -> None:
        """初始化配置管理器并加载配置文件。

        Args:
            config_path: YAML 配置文件的路径

        Raises:
            AidException: 配置文件不存在或格式错误时抛出
        """
        self._config_path: str = config_path
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """从文件系统读取并解析 YAML 配置。

        Raises:
            AidException: 文件不存在或 YAML 格式错误时抛出
        """
        if not os.path.exists(self._config_path):
            raise AidException(
                ErrorCode.INTERNAL_ERROR.code,
                f"配置文件不存在：{self._config_path}",
            )

        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                loaded = yaml.safe_load(f)
                self._config = loaded if isinstance(loaded, dict) else {}
        except yaml.YAMLError as exc:
            raise AidException(
                ErrorCode.INTERNAL_ERROR.code,
                f"配置文件格式错误：{exc}",
            ) from exc

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """获取配置项的值。

        Args:
            key: 配置键名
            default: 键不存在时返回的默认值

        Returns:
            配置项的字符串值或 default
        """
        value = self._config.get(key, default)
        if value is None:
            return default
        return str(value)

    def get_base_url(self) -> str:
        """获取 AID Service 的基础 URL。

        Returns:
            baseURL 配置值

        Raises:
            AidException: 配置中缺少 baseURL 字段时抛出
        """
        url = self.get('baseURL')
        if not url:
            raise AidException(
                ErrorCode.INTERNAL_ERROR.code,
                "配置文件中缺少必填字段：baseURL",
            )
        return url

    def get_api_token(self) -> str:
        """获取 API 鉴权 Token。

        Returns:
            api_token 配置值

        Raises:
            AidException: 配置中缺少 api_token 字段时抛出
        """
        token = self.get('api_token')
        if not token:
            raise AidException(
                ErrorCode.INTERNAL_ERROR.code,
                "配置文件中缺少必填字段：api_token",
            )
        return token

    def reload(self) -> None:
        """重新从文件系统读取配置（热更新）。

        Raises:
            AidException: 文件不存在或格式错误时抛出
        """
        self._load()
