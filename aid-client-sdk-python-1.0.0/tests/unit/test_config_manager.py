# -*- coding: utf-8 -*-
"""
ConfigManager 单元测试

覆盖配置文件加载、字段读取、缺失字段报错等场景。
"""

import os
import tempfile
import pytest

from aid_sdk.config.config_manager import ConfigManager
from aid_sdk.common.exceptions import AidException


# -----------------------------------------------------------------------
# 辅助函数：创建临时 YAML 配置文件
# -----------------------------------------------------------------------

def _make_config_file(content: str) -> str:
    """将内容写入临时文件并返回路径。"""
    fd, path = tempfile.mkstemp(suffix='.yml')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


# -----------------------------------------------------------------------
# 测试用例
# -----------------------------------------------------------------------

class TestConfigManagerLoadSuccess:
    """测试正常加载配置文件。"""

    def test_load_config_success(self):
        """ConfigManager 应成功加载合法的 YAML 配置文件。"""
        path = _make_config_file('baseURL: "http://localhost:8080"\napi_token: "abc123"\n')
        try:
            cm = ConfigManager(path)
            assert cm.get('baseURL') == 'http://localhost:8080'
            assert cm.get('api_token') == 'abc123'
        finally:
            os.unlink(path)

    def test_get_base_url(self):
        """get_base_url() 应返回配置中的 baseURL 值。"""
        path = _make_config_file('baseURL: "http://127.0.0.1:9090/svc"\napi_token: "tok"\n')
        try:
            cm = ConfigManager(path)
            assert cm.get_base_url() == 'http://127.0.0.1:9090/svc'
        finally:
            os.unlink(path)

    def test_get_api_token(self):
        """get_api_token() 应返回配置中的 api_token 值。"""
        path = _make_config_file('baseURL: "http://x"\napi_token: "my-secret-token"\n')
        try:
            cm = ConfigManager(path)
            assert cm.get_api_token() == 'my-secret-token'
        finally:
            os.unlink(path)

    def test_get_with_default(self):
        """get() 在键不存在时应返回指定的默认值。"""
        path = _make_config_file('baseURL: "http://x"\napi_token: "tok"\n')
        try:
            cm = ConfigManager(path)
            result = cm.get('nonexistent_key', 'default_val')
            assert result == 'default_val'
        finally:
            os.unlink(path)

    def test_get_missing_key_returns_none(self):
        """get() 在键不存在且无默认值时应返回 None。"""
        path = _make_config_file('baseURL: "http://x"\napi_token: "tok"\n')
        try:
            cm = ConfigManager(path)
            assert cm.get('missing') is None
        finally:
            os.unlink(path)


class TestConfigManagerErrors:
    """测试配置文件异常场景。"""

    def test_load_config_file_not_found(self):
        """配置文件不存在时应抛出 AidException。"""
        with pytest.raises(AidException) as exc_info:
            ConfigManager('/nonexistent/path/config.yml')
        assert exc_info.value.error_code == 500

    def test_missing_required_field_base_url(self):
        """配置文件中缺少 baseURL 时 get_base_url() 应抛出 AidException。"""
        path = _make_config_file('api_token: "tok"\n')
        try:
            cm = ConfigManager(path)
            with pytest.raises(AidException) as exc_info:
                cm.get_base_url()
            assert exc_info.value.error_code == 500
        finally:
            os.unlink(path)

    def test_missing_required_field_api_token(self):
        """配置文件中缺少 api_token 时 get_api_token() 应抛出 AidException。"""
        path = _make_config_file('baseURL: "http://x"\n')
        try:
            cm = ConfigManager(path)
            with pytest.raises(AidException) as exc_info:
                cm.get_api_token()
            assert exc_info.value.error_code == 500
        finally:
            os.unlink(path)

    def test_reload_updates_config(self):
        """reload() 后应能读取到更新的配置值。"""
        path = _make_config_file('baseURL: "http://old"\napi_token: "old_token"\n')
        try:
            cm = ConfigManager(path)
            assert cm.get_base_url() == 'http://old'
            # 更新配置文件
            with open(path, 'w', encoding='utf-8') as f:
                f.write('baseURL: "http://new"\napi_token: "new_token"\n')
            cm.reload()
            assert cm.get_base_url() == 'http://new'
            assert cm.get_api_token() == 'new_token'
        finally:
            os.unlink(path)
