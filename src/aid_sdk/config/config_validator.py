# -*- coding: utf-8 -*-
"""
配置校验模块

对已加载的配置内容进行必填字段校验。
"""

from aid_sdk.common.exceptions import AidException
from aid_sdk.common.error_codes import ErrorCode
from aid_sdk.config.config_manager import ConfigManager


class ConfigValidator:
    """配置校验器。

    对 ConfigManager 中已加载的配置进行合法性校验，
    确保必填字段存在且不为空。
    """

    # 必填字段列表
    REQUIRED_FIELDS = ['baseURL', 'api_token']

    def validate(self, config: ConfigManager) -> bool:
        """校验配置对象中必填字段是否完整。

        Args:
            config: 已初始化的 ConfigManager 实例

        Returns:
            校验通过时返回 True

        Raises:
            AidException: 缺少必填字段时抛出，错误信息为中文
        """
        for field_name in self.REQUIRED_FIELDS:
            value = config.get(field_name)
            if not value:
                raise AidException(
                    ErrorCode.INTERNAL_ERROR.code,
                    f"配置校验失败：缺少必填字段 '{field_name}'",
                )
        return True
