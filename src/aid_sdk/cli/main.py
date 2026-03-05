# -*- coding: utf-8 -*-
"""
CLI 主入口

定义顶级 Click 命令组，支持通过 --config 指定配置文件路径。
"""

import click


@click.group()
@click.option(
    '--config',
    default='./config/config.yml',
    show_default=True,
    help='配置文件路径',
)
@click.pass_context
def aid(ctx: click.Context, config: str) -> None:
    """AID Client SDK 命令行工具 - 金属加工仿真系统客户端"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config


if __name__ == '__main__':
    aid()
