# -*- coding: utf-8 -*-
"""
HTTP 客户端模块

封装对 AID Service REST API 的 HTTP 请求，支持 JSON POST、
multipart 文件上传和二进制文件下载。
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import requests

from aid_sdk.common.exceptions import AidException
from aid_sdk.common.error_codes import ErrorCode
from aid_sdk.common.response import AidResponse


class HttpClient:
    """AID Service HTTP 客户端。

    封装底层 requests 调用，统一处理鉴权注入、错误转换和响应解析。

    Attributes:
        _base_url: 服务基础 URL，不含末尾斜杠
        _auth_manager: 可选的鉴权管理器，用于注入 apiKey
    """

    # 请求超时时间（秒）
    TIMEOUT = 30

    def __init__(self, base_url: str, auth_manager: Optional[Any] = None) -> None:
        """初始化 HTTP 客户端。

        Args:
            base_url: AID Service 基础 URL（如 http://127.0.0.1:8080/aid-service）
            auth_manager: 可选的鉴权管理器实例（实现 get_auth_token 方法）
        """
        self._base_url: str = base_url.rstrip('/')
        self._auth_manager: Optional[Any] = auth_manager

    def _get_auth_headers(self) -> Dict[str, str]:
        """构建包含 apiKey 的请求头字典。

        Returns:
            含 apiKey header 的字典（无 auth_manager 时返回空字典）
        """
        headers: Dict[str, str] = {}
        if self._auth_manager is not None:
            try:
                headers['apiKey'] = self._auth_manager.get_auth_token()
            except Exception:
                pass
        return headers

    def _inject_api_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """将 apiKey 注入请求参数字典中。

        Args:
            params: 原始请求参数字典

        Returns:
            注入 apiKey 后的参数字典（原字典不被修改）
        """
        merged = dict(params)
        if self._auth_manager is not None:
            try:
                merged['api_key'] = self._auth_manager.get_auth_token()
            except Exception:
                # 获取 Token 失败时不阻断请求，由服务端返回鉴权错误
                pass
        return merged

    def post(self, path: str, params: Dict[str, Any]) -> AidResponse:
        """发送 JSON 格式的 POST 请求。

        Args:
            path: 相对于 base_url 的请求路径（如 /task/create）
            params: 请求体参数字典

        Returns:
            解析后的 AidResponse 实例

        Raises:
            AidException: 网络异常或响应解析失败时抛出
        """
        url = f"{self._base_url}{path}"
        body = self._inject_api_key(params)

        try:
            resp = requests.post(url, json=body, headers=self._get_auth_headers(), timeout=self.TIMEOUT)
            return self._parse_response(resp)
        except requests.exceptions.ConnectionError as exc:
            raise AidException(
                ErrorCode.INTERNAL_ERROR.code,
                f"连接 AID Service 失败，请检查服务地址：{url}",
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise AidException(
                ErrorCode.INTERNAL_ERROR.code,
                f"请求超时（超过 {self.TIMEOUT} 秒）：{url}",
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise AidException(
                ErrorCode.INTERNAL_ERROR.code,
                f"HTTP 请求异常：{exc}",
            ) from exc

    def post_multipart(
        self,
        path: str,
        params: Dict[str, Any],
        files: Union[Dict[str, str], List[Tuple[str, str]]],
    ) -> AidResponse:
        """发送 multipart/form-data 格式的 POST 请求（含文件上传）。

        Args:
            path: 相对路径
            params: 表单参数字典（字段名 -> 值）
            files: 文件列表，两种格式均支持：
                   - List[Tuple[str, str]]：[(文件名, 文件路径), ...]，所有文件统一用字段名 'files'
                   - Dict[str, str]：{字段名: 文件路径}（兼容旧调用，字段名即 key）

        Returns:
            解析后的 AidResponse 实例

        Raises:
            AidException: 文件不存在、网络异常或响应解析失败时抛出
        """
        import os
        url = f"{self._base_url}{path}"
        # 不再把 api_key 注入 form_data，服务端已改为从 header 读取
        form_data = dict(params)

        open_files = []
        try:
            file_tuples = []

            if isinstance(files, list):
                # List[(filename, filepath)] 格式 —— 统一使用字段名 'files'
                for filename, file_path in files:
                    if not os.path.exists(file_path):
                        raise AidException(
                            ErrorCode.FILE_UPLOAD_FAILED.code,
                            f"上传文件不存在：{file_path}",
                        )
                    f = open(file_path, 'rb')
                    open_files.append(f)
                    file_tuples.append(('files', (filename, f)))
            else:
                # Dict[field_name, filepath] 格式（兼容旧接口）
                for field_name, file_path in files.items():
                    if not os.path.exists(file_path):
                        raise AidException(
                            ErrorCode.FILE_UPLOAD_FAILED.code,
                            f"上传文件不存在：{file_path}",
                        )
                    f = open(file_path, 'rb')
                    open_files.append(f)
                    file_tuples.append((field_name, (os.path.basename(file_path), f)))

            resp = requests.post(
                url,
                data=form_data,
                files=file_tuples,
                headers=self._get_auth_headers(),
                timeout=self.TIMEOUT,
            )
            return self._parse_response(resp)
        except AidException:
            raise
        except requests.exceptions.ConnectionError as exc:
            raise AidException(
                ErrorCode.FILE_UPLOAD_FAILED.code,
                f"上传文件时连接 AID Service 失败：{url}",
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise AidException(
                ErrorCode.FILE_UPLOAD_FAILED.code,
                f"上传文件请求超时（超过 {self.TIMEOUT} 秒）",
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise AidException(
                ErrorCode.FILE_UPLOAD_FAILED.code,
                f"上传文件 HTTP 请求异常：{exc}",
            ) from exc
        finally:
            for f in open_files:
                f.close()

    def download(self, path: str, params: Dict[str, Any]) -> bytes:
        """发送 POST 请求并下载二进制响应内容。

        Args:
            path: 相对路径
            params: 请求参数字典

        Returns:
            响应的原始字节内容

        Raises:
            AidException: 网络异常或下载失败时抛出
        """
        url = f"{self._base_url}{path}"
        body = self._inject_api_key(params)

        try:
            resp = requests.post(url, json=body, timeout=self.TIMEOUT, stream=True)
            if resp.status_code != 200:
                raise AidException(
                    ErrorCode.RESULT_FETCH_FAILED.code,
                    f"下载文件失败，HTTP 状态码：{resp.status_code}",
                )
            # 服务端错误响应 HTTP 状态码也是 200，需检查 Content-Type
            content_type = resp.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                try:
                    data = resp.json()
                    code = data.get('code', -1)
                    message = data.get('message', str(data))
                    raise AidException(
                        ErrorCode.RESULT_FETCH_FAILED.code,
                        f"服务端拒绝下载 (code={code}): {message}",
                    )
                except AidException:
                    raise
                except Exception:
                    raise AidException(
                        ErrorCode.RESULT_FETCH_FAILED.code,
                        f"服务端返回异常 JSON: {resp.text[:200]}",
                    )
            return resp.content
        except AidException:
            raise
        except requests.exceptions.ConnectionError as exc:
            raise AidException(
                ErrorCode.RESULT_FETCH_FAILED.code,
                f"下载文件时连接 AID Service 失败：{url}",
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise AidException(
                ErrorCode.RESULT_FETCH_FAILED.code,
                f"下载文件请求超时（超过 {self.TIMEOUT} 秒）",
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise AidException(
                ErrorCode.RESULT_FETCH_FAILED.code,
                f"下载文件 HTTP 请求异常：{exc}",
            ) from exc

    @staticmethod
    def _parse_response(resp: requests.Response) -> AidResponse:
        """将 HTTP 响应解析为 AidResponse 对象。

        Args:
            resp: requests 响应对象

        Returns:
            解析后的 AidResponse 实例

        Raises:
            AidException: 响应不是合法 JSON 时抛出
        """
        try:
            data = resp.json()
        except ValueError as exc:
            raise AidException(
                ErrorCode.INTERNAL_ERROR.code,
                f"响应内容不是合法 JSON，HTTP 状态码：{resp.status_code}",
            ) from exc

        code = data.get('code', resp.status_code)
        message = data.get('message', data.get('msg', ''))
        payload = data.get('data', data)

        return AidResponse(code=int(code), message=str(message), data=payload)
