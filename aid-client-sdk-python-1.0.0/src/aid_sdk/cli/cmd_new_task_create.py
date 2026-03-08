# -*- coding: utf-8 -*-
"""
aid-newTaskCreate CLI 命令

用于创建新的仿真任务。
"""

import sys
import click

from aid_sdk.cli.base import get_client, print_json, print_error
from aid_sdk.common.exceptions import AidException


@click.command('newTaskCreate')
@click.option('--simulateType', 'simulate_type', required=True,
              help='仿真类型（如 LaWan、ZhuZao 等）')
@click.option('--taskName', 'task_name', required=True,
              help='任务名称（1~64 位字母/数字/下划线）')
@click.option('--config', default='./config/config.yml', show_default=True,
              help='配置文件路径')
def newTaskCreate(simulate_type: str, task_name: str, config: str) -> None:
    """创建新的仿真任务。"""
    client = get_client(config)
    try:
        resp = client.new_task_create(simulate_type, task_name)
        print_json(resp.to_dict())
        if not resp.success:
            sys.exit(1)
    except AidException as exc:
        print_error(exc.error_code, exc.error_message)
        sys.exit(1)


def main() -> None:
    """CLI 入口函数。"""
    newTaskCreate()


if __name__ == '__main__':
    main()
