# -*- coding: utf-8 -*-
"""
Multipart 上传辅助模块

提供文件合法性校验和 multipart 格式准备功能，
支持文件类型、大小限制等校验规则。
"""

import os
from typing import List, Set, Tuple

from aid_sdk.common.exceptions import AidException
from aid_sdk.common.error_codes import ErrorCode


class MultipartHelper:
    """Multipart 文件上传辅助类。

    负责验证待上传文件的扩展名、单文件大小和总大小，
    并将文件列表转换为 requests 可用的 multipart 元组格式。
    """

    # 允许上传的文件扩展名（小写）
    ALLOWED_EXTENSIONS: Set[str] = {'stp', 'txt', 'csv', 'yml', 'jnl'}

    # 单文件最大限制：100 MB
    MAX_SINGLE_FILE_SIZE: int = 100 * 1024 * 1024

    # 总文件最大限制：500 MB
    MAX_TOTAL_FILE_SIZE: int = 500 * 1024 * 1024

    def validate_files(self, file_paths: List[str]) -> bool:
        """校验文件列表是否满足上传要求。

        校验规则：
        1. 文件必须存在
        2. 扩展名必须在允许列表中
        3. 单文件不超过 100 MB
        4. 所有文件总大小不超过 500 MB

        Args:
            file_paths: 待上传文件的绝对路径列表

        Returns:
            校验通过时返回 True

        Raises:
            AidException: 任意文件不满足条件时抛出，错误信息为中文
        """
        total_size = 0

        for file_path in file_paths:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise AidException(
                    ErrorCode.FILE_UPLOAD_FAILED.code,
                    f"文件不存在：{file_path}",
                )

            # 检查文件扩展名
            ext = os.path.splitext(file_path)[1].lstrip('.').lower()
            if ext not in self.ALLOWED_EXTENSIONS:
                raise AidException(
                    ErrorCode.FILE_UPLOAD_FAILED.code,
                    f"不支持的文件类型 '.{ext}'，允许类型：{sorted(self.ALLOWED_EXTENSIONS)}",
                )

            # 检查单文件大小
            file_size = os.path.getsize(file_path)
            if file_size > self.MAX_SINGLE_FILE_SIZE:
                size_mb = file_size / (1024 * 1024)
                raise AidException(
                    ErrorCode.FILE_UPLOAD_FAILED.code,
                    f"文件 '{os.path.basename(file_path)}' 大小 {size_mb:.1f} MB 超过单文件上限 100 MB",
                )

            total_size += file_size

        # 检查总大小
        if total_size > self.MAX_TOTAL_FILE_SIZE:
            total_mb = total_size / (1024 * 1024)
            raise AidException(
                ErrorCode.FILE_UPLOAD_FAILED.code,
                f"所有文件总大小 {total_mb:.1f} MB 超过上限 500 MB",
            )

        return True

    def prepare_files(self, file_paths: List[str]) -> List[Tuple]:
        """将文件路径列表转换为 requests multipart 所需的元组格式。

        先执行 validate_files 校验，通过后生成格式化元组。

        Args:
            file_paths: 待上传文件的路径列表

        Returns:
            形如 [('file', (filename, file_bytes, content_type)), ...] 的列表

        Raises:
            AidException: 文件校验失败时抛出
        """
        self.validate_files(file_paths)

        result: List[Tuple] = []
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            with open(file_path, 'rb') as f:
                content = f.read()
            result.append(('file', (file_name, content, 'application/octet-stream')))

        return result
