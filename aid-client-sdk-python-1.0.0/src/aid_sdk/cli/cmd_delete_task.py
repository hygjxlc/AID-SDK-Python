# -*- coding: utf-8 -*-
"""
aid-deleteTask CLI 命令

用于删除指定的仿真任务。
"""

import sys
import click

from aid_sdk.cli.base import get_client, print_json, print_error
from aid_sdk.common.exceptions import AidException


@click.command('deleteTask')
@click.option('--TaskID', 'task_id', required=True, help='目标任务 ID')
@click.option('--config', default='./config/config.yml', show_default=True,
              help='配置文件路径')
def deleteTask(task_id: str, config: str) -> None:
    """删除指定的仿真任务。"""
    client = get_client(config)
    try:
        resp = client.delete_task(task_id)
        print_json(resp.to_dict())
        if not resp.success:
            sys.exit(1)
    except AidException as exc:
        print_error(exc.error_code, exc.error_message)
        sys.exit(1)


def main() -> None:
    """CLI 入口函数。"""
    deleteTask()


if __name__ == '__main__':
    main()
