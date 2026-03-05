# -*- coding: utf-8 -*-
"""
AID Client SDK 门面类

提供统一的 SDK 入口，内部自动完成配置加载、鉴权初始化和
HTTP 客户端创建，并将所有任务操作委托给 TaskService。
"""

from typing import List

from aid_sdk.config.config_manager import ConfigManager
from aid_sdk.config.config_validator import ConfigValidator
from aid_sdk.auth.auth_manager import ApiKeyAuthManager
from aid_sdk.http.http_client import HttpClient
from aid_sdk.task.task_service import TaskService
from aid_sdk.common.response import AidResponse


class AidClient:
    """AID Client SDK 门面类。

    封装 ConfigManager、ApiKeyAuthManager、HttpClient 和 TaskService 的
    创建与组装，对外提供简洁的任务操作接口。

    Attributes:
        _config: 配置管理器
        _auth: 鉴权管理器
        _task_service: 任务服务实例
    """

    def __init__(self, config_path: str = './config/config.yml') -> None:
        """初始化 AID 客户端。

        Args:
            config_path: YAML 配置文件路径，默认为 './config/config.yml'

        Raises:
            AidException: 配置文件不存在、格式错误或缺少必填字段时抛出
        """
        # 加载并校验配置
        self._config: ConfigManager = ConfigManager(config_path)
        validator = ConfigValidator()
        validator.validate(self._config)

        # 初始化鉴权管理器
        self._auth: ApiKeyAuthManager = ApiKeyAuthManager(self._config)

        # 初始化 HTTP 客户端
        http_client = HttpClient(
            base_url=self._config.get_base_url(),
            auth_manager=self._auth,
        )

        # 初始化任务服务
        self._task_service: TaskService = TaskService(http_client)

    # ------------------------------------------------------------------
    # 属性访问器
    # ------------------------------------------------------------------

    @property
    def config(self) -> ConfigManager:
        """返回配置管理器实例。"""
        return self._config

    @property
    def auth(self) -> ApiKeyAuthManager:
        """返回鉴权管理器实例。"""
        return self._auth

    @property
    def task_service(self) -> TaskService:
        """返回任务服务实例。"""
        return self._task_service

    # ------------------------------------------------------------------
    # 任务操作委托方法
    # ------------------------------------------------------------------

    def new_task_create(self, simulate_type: str, task_name: str) -> AidResponse:
        """新建仿真任务。

        Args:
            simulate_type: 仿真类型（如 'LaWan'、'ZhuZao' 等）
            task_name: 任务名称（1~64 位字母/数字/下划线）

        Returns:
            包含 TaskCreateResponse 的 AidResponse
        """
        return self._task_service.new_task_create(simulate_type, task_name)

    def upload_param_files(self, task_id: str, file_paths: List[str]) -> AidResponse:
        """上传任务参数文件。

        Args:
            task_id: 目标任务 ID
            file_paths: 待上传文件的本地路径列表

        Returns:
            包含 UploadFilesResponse 的 AidResponse
        """
        return self._task_service.upload_param_files(task_id, file_paths)

    def new_task_verify(self, task_id: str) -> AidResponse:
        """校验任务参数文件是否完整。

        Args:
            task_id: 目标任务 ID

        Returns:
            包含 VerifyResponse 的 AidResponse
        """
        return self._task_service.new_task_verify(task_id)

    def start_task(self, task_id: str) -> AidResponse:
        """启动仿真任务。

        Args:
            task_id: 目标任务 ID

        Returns:
            包含 TaskStatusResponse 的 AidResponse
        """
        return self._task_service.start_task(task_id)

    def query_task_status(self, task_id: str) -> AidResponse:
        """查询任务当前状态。

        Args:
            task_id: 目标任务 ID

        Returns:
            包含 TaskStatusResponse 的 AidResponse
        """
        return self._task_service.query_task_status(task_id)

    def stop_task(self, task_id: str) -> AidResponse:
        """停止正在运行的任务。

        Args:
            task_id: 目标任务 ID

        Returns:
            包含 TaskStatusResponse 的 AidResponse
        """
        return self._task_service.stop_task(task_id)

    def delete_task(self, task_id: str) -> AidResponse:
        """删除指定任务。

        Args:
            task_id: 目标任务 ID

        Returns:
            包含 TaskStatusResponse 的 AidResponse
        """
        return self._task_service.delete_task(task_id)

    def fetch_task_result(self, task_id: str, output_path: str) -> AidResponse:
        """下载任务结果文件并保存到本地。

        Args:
            task_id: 目标任务 ID
            output_path: 结果文件保存路径（含文件名）

        Returns:
            包含 TaskResultResponse 的 AidResponse
        """
        return self._task_service.fetch_task_result(task_id, output_path)
