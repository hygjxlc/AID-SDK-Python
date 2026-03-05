# -*- coding: utf-8 -*-
"""
TaskService 单元测试

使用 responses 库 Mock HTTP 请求，覆盖所有 8 个任务 API 方法，
以及参数校验的异常路径。
"""

import os
import json
import tempfile
import pytest
import responses as responses_lib

from aid_sdk.http.http_client import HttpClient
from aid_sdk.task.task_service import TaskService
from aid_sdk.common.exceptions import AidException

# 基础 URL（测试用）
BASE_URL = 'http://test-aid-service:8080/aid-service'


# -----------------------------------------------------------------------
# 测试夹具
# -----------------------------------------------------------------------

@pytest.fixture()
def task_service():
    """提供一个不带鉴权的 TaskService 实例（纯单元测试）。"""
    http = HttpClient(base_url=BASE_URL)
    return TaskService(http)


def _json_resp(data: dict, status: int = 200):
    """构造 responses 库所需的 JSON 响应体字符串。"""
    return json.dumps(data)


# -----------------------------------------------------------------------
# newTaskCreate 测试
# -----------------------------------------------------------------------

class TestNewTaskCreate:
    """新建任务 API 测试套件。"""

    @responses_lib.activate
    def test_new_task_create_success(self, task_service):
        """成功新建任务时应返回 code=200 且 data 包含 taskID。"""
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/newTaskCreate',
            body=_json_resp({'code': 200, 'message': '任务创建成功', 'data': {'taskID': 'T001'}}),
            content_type='application/json',
        )
        resp = task_service.new_task_create('LaWan', 'myTask001')
        assert resp.success
        assert resp.code == 200
        assert resp.data.task_id == 'T001'

    def test_new_task_create_invalid_type(self, task_service):
        """不支持的仿真类型应抛出 AidException（code=301）。"""
        with pytest.raises(AidException) as exc_info:
            task_service.new_task_create('InvalidType', 'myTask')
        assert exc_info.value.error_code == 301

    def test_new_task_create_invalid_name_empty(self, task_service):
        """空任务名称应抛出 AidException（code=301）。"""
        with pytest.raises(AidException) as exc_info:
            task_service.new_task_create('LaWan', '')
        assert exc_info.value.error_code == 301

    def test_new_task_create_invalid_name_special_chars(self, task_service):
        """包含特殊字符的任务名称应抛出 AidException（code=301）。"""
        with pytest.raises(AidException) as exc_info:
            task_service.new_task_create('LaWan', 'invalid name!')
        assert exc_info.value.error_code == 301

    def test_new_task_create_invalid_name_too_long(self, task_service):
        """超过 64 字符的任务名称应抛出 AidException。"""
        long_name = 'a' * 65
        with pytest.raises(AidException) as exc_info:
            task_service.new_task_create('LaWan', long_name)
        assert exc_info.value.error_code == 301


# -----------------------------------------------------------------------
# uploadParamFiles 测试
# -----------------------------------------------------------------------

class TestUploadParamFiles:
    """上传参数文件 API 测试套件。"""

    @responses_lib.activate
    def test_upload_param_files_success(self, task_service):
        """成功上传文件时应返回 code=200。"""
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/uploadParamfiles',
            body=_json_resp({
                'code': 200,
                'message': '上传成功',
                'data': {'taskID': 'T001', 'fileList': ['model.stp']},
            }),
            content_type='application/json',
        )
        # 创建临时 .stp 文件
        fd, path = tempfile.mkstemp(suffix='.stp')
        os.close(fd)
        try:
            resp = task_service.upload_param_files('T001', [path])
            assert resp.success
            assert resp.code == 200
        finally:
            os.unlink(path)


# -----------------------------------------------------------------------
# newTaskVerify 测试
# -----------------------------------------------------------------------

class TestNewTaskVerify:
    """任务文件校验 API 测试套件。"""

    @responses_lib.activate
    def test_new_task_verify_success(self, task_service):
        """文件完整时应返回 ready=True。"""
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/newTaskverify',
            body=_json_resp({
                'code': 200,
                'message': '校验通过',
                'data': {'taskID': 'T001', 'ready': True, 'leftFileList': []},
            }),
            content_type='application/json',
        )
        resp = task_service.new_task_verify('T001')
        assert resp.success
        assert resp.data.ready is True
        assert resp.data.left_file_list == []

    @responses_lib.activate
    def test_new_task_verify_not_ready(self, task_service):
        """文件缺失时 ready 应为 False 且 leftFileList 非空。"""
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/newTaskverify',
            body=_json_resp({
                'code': 200,
                'message': '文件缺失',
                'data': {'taskID': 'T001', 'ready': False, 'leftFileList': ['missing.txt']},
            }),
            content_type='application/json',
        )
        resp = task_service.new_task_verify('T001')
        assert resp.success
        assert resp.data.ready is False
        assert 'missing.txt' in resp.data.left_file_list


# -----------------------------------------------------------------------
# startTask 测试
# -----------------------------------------------------------------------

class TestStartTask:
    """启动任务 API 测试套件。"""

    @responses_lib.activate
    def test_start_task_success(self, task_service):
        """成功启动任务时应返回 code=200 且 status 非空。"""
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/startTask',
            body=_json_resp({
                'code': 200,
                'message': '任务已启动',
                'data': {'taskID': 'T001', 'status': 'running'},
            }),
            content_type='application/json',
        )
        resp = task_service.start_task('T001')
        assert resp.success
        assert resp.data.status == 'running'


# -----------------------------------------------------------------------
# queryTaskStatus 测试
# -----------------------------------------------------------------------

class TestQueryTaskStatus:
    """查询任务状态 API 测试套件。"""

    @responses_lib.activate
    def test_query_task_status_success(self, task_service):
        """成功查询任务状态时应返回 code=200。"""
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/queryTaskStatus',
            body=_json_resp({
                'code': 200,
                'message': '查询成功',
                'data': {'taskID': 'T001', 'status': 'finished', 'extraInfo': None},
            }),
            content_type='application/json',
        )
        resp = task_service.query_task_status('T001')
        assert resp.success
        assert resp.data.status == 'finished'


# -----------------------------------------------------------------------
# stopTask 测试
# -----------------------------------------------------------------------

class TestStopTask:
    """停止任务 API 测试套件。"""

    @responses_lib.activate
    def test_stop_task_success(self, task_service):
        """成功停止任务时应返回 code=200。"""
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/stopTask',
            body=_json_resp({
                'code': 200,
                'message': '任务已停止',
                'data': {'taskID': 'T001', 'status': 'stopped'},
            }),
            content_type='application/json',
        )
        resp = task_service.stop_task('T001')
        assert resp.success
        assert resp.data.status == 'stopped'


# -----------------------------------------------------------------------
# deleteTask 测试
# -----------------------------------------------------------------------

class TestDeleteTask:
    """删除任务 API 测试套件。"""

    @responses_lib.activate
    def test_delete_task_success(self, task_service):
        """成功删除任务时应返回 code=200。"""
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/deleteTask',
            body=_json_resp({
                'code': 200,
                'message': '任务已删除',
                'data': {'taskID': 'T001', 'status': 'deleted'},
            }),
            content_type='application/json',
        )
        resp = task_service.delete_task('T001')
        assert resp.success
        assert resp.data.status == 'deleted'


# -----------------------------------------------------------------------
# fetchTaskResult 测试
# -----------------------------------------------------------------------

class TestFetchTaskResult:
    """获取任务结果 API 测试套件。"""

    @responses_lib.activate
    def test_fetch_task_result_success(self, task_service):
        """成功下载任务结果时应将内容写入指定路径。"""
        fake_content = b'binary result data'
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/fetchTaskResult',
            body=fake_content,
            content_type='application/octet-stream',
            status=200,
        )
        fd, output_path = tempfile.mkstemp(suffix='.zip')
        os.close(fd)
        try:
            resp = task_service.fetch_task_result('T001', output_path)
            assert resp.success
            assert resp.data.result_file_path == output_path
            # 校验文件内容
            with open(output_path, 'rb') as f:
                assert f.read() == fake_content
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_fetch_task_result_empty_output_path(self, task_service):
        """输出路径为空时应抛出 AidException。"""
        with pytest.raises(AidException) as exc_info:
            task_service.fetch_task_result('T001', '')
        assert exc_info.value.error_code == 404
