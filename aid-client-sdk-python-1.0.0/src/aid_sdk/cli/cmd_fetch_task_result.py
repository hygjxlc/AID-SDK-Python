# -*- coding: utf-8 -*-
"""
aid-fetchTaskResult CLI 命令

用于下载仿真任务的结果文件并保存到本地。
"""

import sys
import click

from aid_sdk.cli.base import get_client, print_json, print_error
from aid_sdk.common.exceptions import AidException


@click.command('fetchTaskResult')
@click.option('--TaskID', 'task_id', required=True, help='目标任务 ID')
@click.option('--output', required=True, help='结果文件保存路径（含文件名）')
@click.option('--config', default='./config/config.yml', show_default=True,
              help='配置文件路径')
def fetchTaskResult(task_id: str, output: str, config: str) -> None:
    """下载任务结果文件并保存到本地。"""
    client = get_client(config)
    try:
        resp = client.fetch_task_result(task_id, output)
        print_json(resp.to_dict())
        if not resp.success:
            sys.exit(1)
    except AidException as exc:
        print_error(exc.error_code, exc.error_message)
        sys.exit(1)


def main() -> None:
    """CLI 入口函数。"""
    fetchTaskResult()


if __name__ == '__main__':
    main()
