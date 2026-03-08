# -*- coding: utf-8 -*-
"""
工作流集成测试

使用 responses 库 Mock HTTP，模拟完整的任务生命周期，
验证各 API 调用的顺序正确性和数据传递的完整性。
"""

import os
import json
import tempfile
import pytest
import responses as responses_lib

from aid_sdk.http.http_client import HttpClient
from aid_sdk.task.task_service import TaskService

BASE_URL = 'http://test-aid-service:8080/aid-service'


# -----------------------------------------------------------------------
# 辅助函数
# -----------------------------------------------------------------------

def _json_body(data: dict) -> str:
    """生成 JSON 字符串。"""
    return json.dumps(data)


def _make_task_service() -> TaskService:
    """创建测试用 TaskService。"""
    return TaskService(HttpClient(base_url=BASE_URL))


# -----------------------------------------------------------------------
# 集成测试：完整任务生命周期
# -----------------------------------------------------------------------

class TestFullTaskLifecycle:
    """完整任务生命周期集成测试：创建 -> 上传 -> 校验 -> 启动 -> 查询 -> 停止 -> 删除。"""

    @responses_lib.activate
    def test_full_task_lifecycle(self):
        """模拟一个完整的任务生命周期，各步骤应依次成功。"""
        task_id = 'LIFECYCLE_001'

        # 1. 注册 Mock：新建任务
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/newTaskCreate',
            body=_json_body({
                'code': 200,
                'message': '任务创建成功',
                'data': {'taskID': task_id},
            }),
            content_type='application/json',
        )

        # 2. 注册 Mock：上传文件
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/uploadParamfiles',
            body=_json_body({
                'code': 200,
                'message': '上传成功',
                'data': {'taskID': task_id, 'fileList': ['model.stp']},
            }),
            content_type='application/json',
        )

        # 3. 注册 Mock：校验文件
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/newTaskverify',
            body=_json_body({
                'code': 200,
                'message': '校验通过',
                'data': {'taskID': task_id, 'ready': True, 'leftFileList': []},
            }),
            content_type='application/json',
        )

        # 4. 注册 Mock：启动任务
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/startTask',
            body=_json_body({
                'code': 200,
                'message': '任务已启动',
                'data': {'taskID': task_id, 'status': 'running'},
            }),
            content_type='application/json',
        )

        # 5. 注册 Mock：查询状态
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/queryTaskStatus',
            body=_json_body({
                'code': 200,
                'message': '运行中',
                'data': {'taskID': task_id, 'status': 'running', 'extraInfo': None},
            }),
            content_type='application/json',
        )

        # 6. 注册 Mock：停止任务
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/stopTask',
            body=_json_body({
                'code': 200,
                'message': '任务已停止',
                'data': {'taskID': task_id, 'status': 'stopped'},
            }),
            content_type='application/json',
        )

        # 7. 注册 Mock：删除任务
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/deleteTask',
            body=_json_body({
                'code': 200,
                'message': '任务已删除',
                'data': {'taskID': task_id, 'status': 'deleted'},
            }),
            content_type='application/json',
        )

        # 执行完整生命周期
        svc = _make_task_service()

        # Step 1: 创建任务
        create_resp = svc.new_task_create('LaWan', 'lifecycle_task')
        assert create_resp.success, f"创建任务失败：{create_resp.message}"
        assert create_resp.data.task_id == task_id

        # Step 2: 上传文件（使用临时 .stp 文件）
        fd, stp_path = tempfile.mkstemp(suffix='.stp')
        os.close(fd)
        try:
            upload_resp = svc.upload_param_files(task_id, [stp_path])
            assert upload_resp.success, f"上传文件失败：{upload_resp.message}"
        finally:
            os.unlink(stp_path)

        # Step 3: 校验文件
        verify_resp = svc.new_task_verify(task_id)
        assert verify_resp.success, f"文件校验失败：{verify_resp.message}"
        assert verify_resp.data.ready is True

        # Step 4: 启动任务
        start_resp = svc.start_task(task_id)
        assert start_resp.success, f"启动任务失败：{start_resp.message}"
        assert start_resp.data.status == 'running'

        # Step 5: 查询状态
        status_resp = svc.query_task_status(task_id)
        assert status_resp.success, f"查询状态失败：{status_resp.message}"
        assert status_resp.data.status == 'running'

        # Step 6: 停止任务
        stop_resp = svc.stop_task(task_id)
        assert stop_resp.success, f"停止任务失败：{stop_resp.message}"
        assert stop_resp.data.status == 'stopped'

        # Step 7: 删除任务
        delete_resp = svc.delete_task(task_id)
        assert delete_resp.success, f"删除任务失败：{delete_resp.message}"
        assert delete_resp.data.status == 'deleted'


# -----------------------------------------------------------------------
# 集成测试：任务结果流
# -----------------------------------------------------------------------

class TestTaskResultFlow:
    """任务结果获取流程集成测试：创建 -> 上传 -> 校验 -> 启动 -> 查询（完成）-> 获取结果。"""

    @responses_lib.activate
    def test_task_result_flow(self):
        """任务完成后应能成功下载结果文件到本地。"""
        task_id = 'RESULT_FLOW_001'
        fake_result_bytes = b'PK compressed result data'

        # 注册 Mock：新建任务
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/newTaskCreate',
            body=_json_body({
                'code': 200,
                'message': '任务创建成功',
                'data': {'taskID': task_id},
            }),
            content_type='application/json',
        )

        # 注册 Mock：上传文件
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/uploadParamfiles',
            body=_json_body({
                'code': 200,
                'message': '上传成功',
                'data': {'taskID': task_id, 'fileList': ['params.txt']},
            }),
            content_type='application/json',
        )

        # 注册 Mock：校验文件
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/newTaskverify',
            body=_json_body({
                'code': 200,
                'message': '校验通过',
                'data': {'taskID': task_id, 'ready': True, 'leftFileList': []},
            }),
            content_type='application/json',
        )

        # 注册 Mock：启动任务
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/startTask',
            body=_json_body({
                'code': 200,
                'message': '任务已启动',
                'data': {'taskID': task_id, 'status': 'running'},
            }),
            content_type='application/json',
        )

        # 注册 Mock：查询状态（已完成）
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/queryTaskStatus',
            body=_json_body({
                'code': 200,
                'message': '任务已完成',
                'data': {'taskID': task_id, 'status': 'finished', 'extraInfo': None},
            }),
            content_type='application/json',
        )

        # 注册 Mock：获取结果（返回二进制内容）
        responses_lib.add(
            responses_lib.POST,
            f'{BASE_URL}/fetchTaskResult',
            body=fake_result_bytes,
            content_type='application/octet-stream',
            status=200,
        )

        svc = _make_task_service()

        # Step 1: 创建任务
        create_resp = svc.new_task_create('ZhuZao', 'result_flow_task')
        assert create_resp.success
        assert create_resp.data.task_id == task_id

        # Step 2: 上传文件（使用临时 .txt 文件）
        fd, txt_path = tempfile.mkstemp(suffix='.txt')
        os.close(fd)
        try:
            upload_resp = svc.upload_param_files(task_id, [txt_path])
            assert upload_resp.success
        finally:
            os.unlink(txt_path)

        # Step 3: 校验文件
        verify_resp = svc.new_task_verify(task_id)
        assert verify_resp.success
        assert verify_resp.data.ready is True

        # Step 4: 启动任务
        start_resp = svc.start_task(task_id)
        assert start_resp.success

        # Step 5: 查询状态（模拟已完成）
        status_resp = svc.query_task_status(task_id)
        assert status_resp.success
        assert status_resp.data.status == 'finished'

        # Step 6: 获取结果文件
        fd2, output_path = tempfile.mkstemp(suffix='.zip')
        os.close(fd2)
        try:
            result_resp = svc.fetch_task_result(task_id, output_path)
            assert result_resp.success, f"获取结果失败：{result_resp.message}"
            assert result_resp.data.result_file_path == output_path

            # 校验写入的内容与 Mock 数据一致
            with open(output_path, 'rb') as f:
                saved_content = f.read()
            assert saved_content == fake_result_bytes
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
