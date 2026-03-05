# -*- coding: utf-8 -*-
"""
任务管理服务模块

封装所有任务相关 REST API 的调用逻辑，包含参数校验、
HTTP 请求、响应解析和结构化日志记录。
"""

import os
import re
from typing import List

from aid_sdk.common.exceptions import AidException
from aid_sdk.common.error_codes import ErrorCode
from aid_sdk.common.response import AidResponse
from aid_sdk.http.http_client import HttpClient
from aid_sdk.http.multipart_helper import MultipartHelper
from aid_sdk.logging.aid_logger import get_logger, log_api_call
from aid_sdk.task.models import (
    TaskCreateResponse,
    UploadFilesResponse,
    VerifyResponse,
    TaskStatusResponse,
    TaskResultResponse,
)

logger = get_logger(__name__)


class TaskService:
    """任务管理服务类。

    封装对 AID Service 任务相关 API 的全部调用，
    每个方法对应一个 API 端点。

    Attributes:
        _http: HttpClient 实例
        _multipart_helper: MultipartHelper 实例
    """

    # 支持的仿真类型列表
    ALLOWED_SIMULATE_TYPES: List[str] = [
        'LaWan', 'CHOnYA', 'ZhuZao', 'ZhaZhi', 'ZHEWan', 'JIYA'
    ]

    # 任务名称合法字符正则（1~64位，字母/数字/下划线）
    _TASK_NAME_PATTERN = re.compile(r'^[A-Za-z0-9_]{1,64}$')

    def __init__(self, http_client: HttpClient) -> None:
        """初始化任务服务。

        Args:
            http_client: 已配置的 HttpClient 实例
        """
        self._http: HttpClient = http_client
        self._multipart_helper: MultipartHelper = MultipartHelper()

    # ------------------------------------------------------------------
    # 参数校验辅助方法
    # ------------------------------------------------------------------

    def _validate_simulate_type(self, simulate_type: str) -> None:
        """校验仿真类型是否在允许列表中。

        Args:
            simulate_type: 仿真类型字符串

        Raises:
            AidException: 仿真类型不合法时抛出
        """
        if simulate_type not in self.ALLOWED_SIMULATE_TYPES:
            raise AidException(
                ErrorCode.TASK_CREATE_FAILED.code,
                f"不支持的仿真类型 '{simulate_type}'，"
                f"允许类型：{self.ALLOWED_SIMULATE_TYPES}",
            )

    def _validate_task_name(self, task_name: str) -> None:
        """校验任务名称是否合法（1~64位字母/数字/下划线）。

        Args:
            task_name: 任务名称字符串

        Raises:
            AidException: 任务名称不合法时抛出
        """
        if not self._TASK_NAME_PATTERN.match(task_name):
            raise AidException(
                ErrorCode.TASK_CREATE_FAILED.code,
                "任务名称只允许字母、数字和下划线，且长度在 1~64 个字符之间",
            )

    def _validate_task_id(self, task_id: str) -> None:
        """校验任务 ID 非空。

        Args:
            task_id: 任务 ID 字符串

        Raises:
            AidException: 任务 ID 为空时抛出
        """
        if not task_id or not task_id.strip():
            raise AidException(
                ErrorCode.RESULT_FETCH_FAILED.code,
                "任务 ID 不能为空",
            )

    # ------------------------------------------------------------------
    # API 方法
    # ------------------------------------------------------------------

    def new_task_create(self, simulate_type: str, task_name: str) -> AidResponse:
        """调用新建任务 API。

        Args:
            simulate_type: 仿真类型，必须在 ALLOWED_SIMULATE_TYPES 中
            task_name: 任务名称，1~64 位字母/数字/下划线

        Returns:
            包含 TaskCreateResponse 的 AidResponse

        Raises:
            AidException: 参数不合法或请求失败时抛出
        """
        self._validate_simulate_type(simulate_type)
        self._validate_task_name(task_name)

        log_api_call(logger, 'newTaskCreate', message=f"创建任务：{task_name}（类型：{simulate_type}）")

        resp = self._http.post('/newTaskCreate', {
            'simulateType': simulate_type,
            'taskName': task_name,
        })

        if resp.success:
            data = resp.data if isinstance(resp.data, dict) else {}
            # 兼容服务端直接在 data 层或顶层返回 taskID
            task_create_resp = TaskCreateResponse.from_dict({
                'code': resp.code,
                'message': resp.message,
                **data,
            })
            log_api_call(logger, 'newTaskCreate', task_id=task_create_resp.task_id,
                         message="任务创建成功")
            return AidResponse(code=resp.code, message=resp.message, data=task_create_resp)

        log_api_call(logger, 'newTaskCreate', message=f"任务创建失败：{resp.message}", level='error')
        return AidResponse.failure_response(resp.code, resp.message)

    def upload_param_files(self, task_id: str, file_paths: List[str]) -> AidResponse:
        """调用上传参数文件 API。

        Args:
            task_id: 目标任务 ID
            file_paths: 待上传文件的本地路径列表

        Returns:
            包含 UploadFilesResponse 的 AidResponse

        Raises:
            AidException: 参数不合法、文件校验失败或请求失败时抛出
        """
        self._validate_task_id(task_id)

        # 文件合法性校验（扩展名、大小）
        self._multipart_helper.validate_files(file_paths)

        log_api_call(logger, 'uploadParamFiles', task_id=task_id,
                     message=f"上传 {len(file_paths)} 个文件")

        # 构建 files 列表：服务端要求所有文件统一使用字段名 'files'
        # 不能用 dict（会去重，导致只保留最后一个文件），必须用列表
        files_list = [(os.path.basename(fp), fp) for fp in file_paths]

        resp = self._http.post_multipart(
            '/uploadParamfiles',
            {'TaskID': task_id},
            files_list,
        )

        if resp.success:
            data = resp.data if isinstance(resp.data, dict) else {}
            upload_resp = UploadFilesResponse.from_dict({
                'code': resp.code,
                'message': resp.message,
                'taskID': task_id,
                **data,
            })
            log_api_call(logger, 'uploadParamFiles', task_id=task_id,
                         message="文件上传成功")
            return AidResponse(code=resp.code, message=resp.message, data=upload_resp)

        log_api_call(logger, 'uploadParamFiles', task_id=task_id,
                     message=f"文件上传失败：{resp.message}", level='error')
        return AidResponse.failure_response(resp.code, resp.message)

    def new_task_verify(self, task_id: str) -> AidResponse:
        """调用任务文件校验 API。

        Args:
            task_id: 目标任务 ID

        Returns:
            包含 VerifyResponse 的 AidResponse
        """
        self._validate_task_id(task_id)
        log_api_call(logger, 'newTaskVerify', task_id=task_id, message="校验任务文件")

        resp = self._http.post('/newTaskverify', {'TaskID': task_id})

        if resp.success:
            data = resp.data if isinstance(resp.data, dict) else {}
            verify_resp = VerifyResponse.from_dict({
                'code': resp.code,
                'message': resp.message,
                'taskID': task_id,
                **data,
            })
            log_api_call(logger, 'newTaskVerify', task_id=task_id,
                         message=f"校验完成，ready={verify_resp.ready}")
            return AidResponse(code=resp.code, message=resp.message, data=verify_resp)

        return AidResponse.failure_response(resp.code, resp.message)

    def start_task(self, task_id: str) -> AidResponse:
        """调用启动任务 API。

        Args:
            task_id: 目标任务 ID

        Returns:
            包含 TaskStatusResponse 的 AidResponse
        """
        self._validate_task_id(task_id)
        log_api_call(logger, 'startTask', task_id=task_id, message="启动任务")

        resp = self._http.post('/startTask', {'TaskID': task_id})

        if resp.success:
            data = resp.data if isinstance(resp.data, dict) else {}
            status_resp = TaskStatusResponse.from_dict({
                'code': resp.code,
                'message': resp.message,
                'taskID': task_id,
                **data,
            })
            log_api_call(logger, 'startTask', task_id=task_id,
                         message=f"任务启动成功，状态：{status_resp.status}")
            return AidResponse(code=resp.code, message=resp.message, data=status_resp)

        return AidResponse.failure_response(resp.code, resp.message)

    def query_task_status(self, task_id: str) -> AidResponse:
        """调用查询任务状态 API。

        Args:
            task_id: 目标任务 ID

        Returns:
            包含 TaskStatusResponse 的 AidResponse
        """
        self._validate_task_id(task_id)
        log_api_call(logger, 'queryTaskStatus', task_id=task_id, message="查询任务状态")

        resp = self._http.post('/queryTaskStatus', {'TaskID': task_id})

        if resp.success:
            data = resp.data if isinstance(resp.data, dict) else {}
            status_resp = TaskStatusResponse.from_dict({
                'code': resp.code,
                'message': resp.message,
                'taskID': task_id,
                **data,
            })
            return AidResponse(code=resp.code, message=resp.message, data=status_resp)

        return AidResponse.failure_response(resp.code, resp.message)

    def stop_task(self, task_id: str) -> AidResponse:
        """调用停止任务 API。

        Args:
            task_id: 目标任务 ID

        Returns:
            包含 TaskStatusResponse 的 AidResponse
        """
        self._validate_task_id(task_id)
        log_api_call(logger, 'stopTask', task_id=task_id, message="停止任务")

        resp = self._http.post('/stopTask', {'TaskID': task_id})

        if resp.success:
            data = resp.data if isinstance(resp.data, dict) else {}
            status_resp = TaskStatusResponse.from_dict({
                'code': resp.code,
                'message': resp.message,
                'taskID': task_id,
                **data,
            })
            log_api_call(logger, 'stopTask', task_id=task_id, message="任务已停止")
            return AidResponse(code=resp.code, message=resp.message, data=status_resp)

        return AidResponse.failure_response(resp.code, resp.message)

    def delete_task(self, task_id: str) -> AidResponse:
        """调用删除任务 API。

        Args:
            task_id: 目标任务 ID

        Returns:
            包含 TaskStatusResponse 的 AidResponse
        """
        self._validate_task_id(task_id)
        log_api_call(logger, 'deleteTask', task_id=task_id, message="删除任务")

        resp = self._http.post('/deleteTask', {'TaskID': task_id})

        if resp.success:
            data = resp.data if isinstance(resp.data, dict) else {}
            status_resp = TaskStatusResponse.from_dict({
                'code': resp.code,
                'message': resp.message,
                'taskID': task_id,
                **data,
            })
            log_api_call(logger, 'deleteTask', task_id=task_id, message="任务已删除")
            return AidResponse(code=resp.code, message=resp.message, data=status_resp)

        return AidResponse.failure_response(resp.code, resp.message)

    def fetch_task_result(self, task_id: str, output_path: str) -> AidResponse:
        """调用获取任务结果 API，并将结果文件保存到本地。

        Args:
            task_id: 目标任务 ID
            output_path: 结果文件保存路径（含文件名）

        Returns:
            包含 TaskResultResponse 的 AidResponse

        Raises:
            AidException: 参数不合法、下载失败或文件写入失败时抛出
        """
        self._validate_task_id(task_id)
        if not output_path or not output_path.strip():
            raise AidException(
                ErrorCode.RESULT_FETCH_FAILED.code,
                "输出文件路径不能为空",
            )

        log_api_call(logger, 'fetchTaskResult', task_id=task_id,
                     message=f"获取任务结果，保存至：{output_path}")

        content = self._http.download('/fetchTaskResult', {'TaskID': task_id})

        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        try:
            with open(output_path, 'wb') as f:
                f.write(content)
        except OSError as exc:
            raise AidException(
                ErrorCode.RESULT_FETCH_FAILED.code,
                f"结果文件写入失败：{exc}",
            ) from exc

        result_resp = TaskResultResponse(
            code=200,
            task_id=task_id,
            message="任务结果获取成功",
            result_file_path=output_path,
        )
        log_api_call(logger, 'fetchTaskResult', task_id=task_id,
                     message=f"结果已保存：{output_path}")
        return AidResponse(code=200, message="任务结果获取成功", data=result_resp)
