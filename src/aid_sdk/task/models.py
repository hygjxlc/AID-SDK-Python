# -*- coding: utf-8 -*-
"""
任务相关数据模型

定义所有任务 API 的请求/响应数据结构，均采用 dataclass 实现，
并提供 from_dict / to_dict 方法便于序列化。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TaskCreateResponse:
    """新建任务接口响应模型。

    Attributes:
        code: 响应状态码
        task_id: 创建成功后的任务 ID
        message: 描述信息
    """

    code: int
    task_id: str
    message: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskCreateResponse':
        """从字典构建响应实例。

        Args:
            data: 响应字典

        Returns:
            TaskCreateResponse 实例
        """
        return cls(
            code=int(data.get('code', 0)),
            task_id=str(data.get('taskID', data.get('task_id', ''))),
            message=str(data.get('message', data.get('msg', ''))),
        )

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。"""
        return {'code': self.code, 'taskID': self.task_id, 'message': self.message}


@dataclass
class UploadFilesResponse:
    """上传参数文件接口响应模型。

    Attributes:
        code: 响应状态码
        task_id: 关联任务 ID
        message: 描述信息
        file_list: 已上传的文件名列表（兼容字段，从 uploadFiles 提取）
        upload_files: 上传成功的文件详情列表（服务端原始字段 uploadFiles）
        fail_files: 上传失败的文件详情列表（服务端原始字段 failFiles）
    """

    code: int
    task_id: str
    message: str
    file_list: List[str] = field(default_factory=list)
    upload_files: List[Dict[str, Any]] = field(default_factory=list)
    fail_files: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UploadFilesResponse':
        """从字典构建响应实例。"""
        # 服务端返回 uploadFiles（List[{filename, size, ...}]）
        upload_files = list(data.get('uploadFiles', data.get('upload_files', [])))
        fail_files = list(data.get('failFiles', data.get('fail_files', [])))
        # 兼容字段：从 uploadFiles 中提取文件名列表
        file_list = [
            str(f.get('filename', f)) if isinstance(f, dict) else str(f)
            for f in upload_files
        ]
        return cls(
            code=int(data.get('code', 0)),
            task_id=str(data.get('taskID', data.get('task_id', ''))),
            message=str(data.get('message', data.get('msg', ''))),
            file_list=file_list,
            upload_files=upload_files,
            fail_files=fail_files,
        )

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。"""
        return {
            'code': self.code,
            'taskID': self.task_id,
            'message': self.message,
            'uploadFiles': self.upload_files,
            'failFiles': self.fail_files,
        }


@dataclass
class VerifyResponse:
    """任务文件校验接口响应模型。

    Attributes:
        code: 响应状态码
        task_id: 关联任务 ID
        ready: 文件是否完整、可开始任务
        left_file_list: 缺失的文件名列表
        message: 描述信息
    """

    code: int
    task_id: str
    ready: bool
    left_file_list: List[str] = field(default_factory=list)
    message: str = ''

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VerifyResponse':
        """从字典构建响应实例。"""
        return cls(
            code=int(data.get('code', 0)),
            task_id=str(data.get('taskID', data.get('task_id', ''))),
            ready=bool(data.get('ready', False)),
            # 服务端返回 missingFiles，兼容 leftFileList / left_file_list
            left_file_list=list(data.get('missingFiles',
                                data.get('leftFileList',
                                data.get('left_file_list', [])))),
            message=str(data.get('message', data.get('msg', ''))),
        )

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。"""
        return {
            'code': self.code,
            'taskID': self.task_id,
            'ready': self.ready,
            'leftFileList': self.left_file_list,
            'message': self.message,
        }


@dataclass
class TaskStatusResponse:
    """任务状态接口响应模型（适用于 start/query/stop/delete）。

    Attributes:
        code: 响应状态码
        task_id: 关联任务 ID
        status: 任务当前状态字符串
        extra_info: 额外信息（可为任意类型）
        message: 描述信息
    """

    code: int
    task_id: str
    status: str
    extra_info: Optional[Any] = None
    message: str = ''

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskStatusResponse':
        """从字典构建响应实例。"""
        return cls(
            code=int(data.get('code', 0)),
            task_id=str(data.get('taskID', data.get('task_id', ''))),
            status=str(data.get('status', '')),
            # 服务端返回 extra（dict），兼容 extraInfo / extra_info
            extra_info=data.get('extra', data.get('extraInfo', data.get('extra_info'))),
            message=str(data.get('message', data.get('msg', ''))),
        )

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。"""
        return {
            'code': self.code,
            'taskID': self.task_id,
            'status': self.status,
            'extraInfo': self.extra_info,
            'message': self.message,
        }


@dataclass
class TaskResultResponse:
    """获取任务结果接口响应模型。

    Attributes:
        code: 响应状态码
        task_id: 关联任务 ID
        message: 描述信息
        result_file_path: 本地保存的结果文件路径
    """

    code: int
    task_id: str
    message: str
    result_file_path: str = ''

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskResultResponse':
        """从字典构建响应实例。"""
        return cls(
            code=int(data.get('code', 0)),
            task_id=str(data.get('taskID', data.get('task_id', ''))),
            message=str(data.get('message', data.get('msg', ''))),
            result_file_path=str(data.get('resultFilePath', data.get('result_file_path', ''))),
        )

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。"""
        return {
            'code': self.code,
            'taskID': self.task_id,
            'message': self.message,
            'resultFilePath': self.result_file_path,
        }
