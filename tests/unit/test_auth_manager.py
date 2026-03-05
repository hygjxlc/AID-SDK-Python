# -*- coding: utf-8 -*-
"""
ApiKeyAuthManager 单元测试

覆盖 Token 获取、Token 验证（合法/非法）和鉴权类型等场景。
"""

import os
import tempfile
import pytest

from aid_sdk.config.config_manager import ConfigManager
from aid_sdk.auth.auth_manager import ApiKeyAuthManager


# -----------------------------------------------------------------------
# 测试夹具
# -----------------------------------------------------------------------

@pytest.fixture()
def config_manager():
    """提供一个临时配置文件的 ConfigManager 实例。"""
    fd, path = tempfile.mkstemp(suffix='.yml')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write('baseURL: "http://127.0.0.1:8080/aid-service"\napi_token: "test-token-abc"\n')
    cm = ConfigManager(path)
    yield cm
    os.unlink(path)


@pytest.fixture()
def auth_manager(config_manager):
    """提供一个 ApiKeyAuthManager 实例。"""
    return ApiKeyAuthManager(config_manager)


# -----------------------------------------------------------------------
# 测试用例
# -----------------------------------------------------------------------

class TestApiKeyAuthManager:
    """ApiKeyAuthManager 测试套件。"""

    def test_get_auth_token(self, auth_manager):
        """get_auth_token() 应返回配置中的 api_token。"""
        token = auth_manager.get_auth_token()
        assert token == 'test-token-abc'

    def test_authenticate_valid(self, auth_manager):
        """传入正确的 Token 时 authenticate() 应返回 True。"""
        assert auth_manager.authenticate('test-token-abc') is True

    def test_authenticate_invalid(self, auth_manager):
        """传入错误的 Token 时 authenticate() 应返回 False。"""
        assert auth_manager.authenticate('wrong-token') is False

    def test_authenticate_empty_token(self, auth_manager):
        """传入空字符串时 authenticate() 应返回 False。"""
        assert auth_manager.authenticate('') is False

    def test_get_auth_type(self, auth_manager):
        """get_auth_type() 应固定返回 'api_key'。"""
        assert auth_manager.get_auth_type() == 'api_key'
