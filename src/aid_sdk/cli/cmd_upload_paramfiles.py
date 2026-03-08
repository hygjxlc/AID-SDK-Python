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
@click.option('--files', required=True, multiple=True,
              help='待上传文件路径，多个文件用空格或英文逗号分隔')
@click.option('--config', default='./config/config.yml', show_default=True,
              help='配置文件路径')
def uploadParamfiles(task_id: str, files: tuple, config: str) -> None:
    """上传任务参数文件。"""
    client = get_client(config)
    # 支持空格分隔（multiple=True 每个 --files 值为一项）和逗号分隔（每项内部再拆分）
    file_paths = []
    for item in files:
        for fp in item.split(','):
            fp = fp.strip()
            if fp:
                file_paths.append(fp)

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
