# -*- coding: utf-8 -*-
"""
aid-uploadParamfiles CLI 命令

用于向指定任务上传参数文件，支持逗号分隔的多文件路径。
"""

import sys
import click

from aid_sdk.cli.base import get_client, print_json, print_error
from aid_sdk.common.exceptions import AidException


@click.command('uploadParamfiles')
@click.option('--TaskID', 'task_id', required=True, help='目标任务 ID')
@click.option('--files', required=True,
              help='待上传文件路径，多个文件用英文逗号分隔')
@click.option('--config', default='./config/config.yml', show_default=True,
              help='配置文件路径')
def uploadParamfiles(task_id: str, files: str, config: str) -> None:
    """上传任务参数文件。"""
    client = get_client(config)
    # 解析逗号分隔的文件列表，去除首尾空格
    file_paths = [fp.strip() for fp in files.split(',') if fp.strip()]

    try:
        resp = client.upload_param_files(task_id, file_paths)
        print_json(resp.to_dict())
        if not resp.success:
            sys.exit(1)
    except AidException as exc:
        print_error(exc.error_code, exc.error_message)
        sys.exit(1)


def main() -> None:
    """CLI 入口函数。"""
    uploadParamfiles()


if __name__ == '__main__':
    main()
