# -*- coding: utf-8 -*-
"""
aid-help CLI 命令

打印所有可用命令及其中文说明。
"""

import click


# 命令帮助信息表（命令名 -> 描述）
COMMANDS_HELP = [
    ('newTaskCreate',
     '新建仿真任务\n'
     '  参数：--simulateType（仿真类型）、--taskName（任务名称）\n'
     '  示例：cli_start.bat newTaskCreate --simulateType LaWan --taskName myTask001'),
    ('uploadParamfiles',
     '上传任务参数文件\n'
     '  参数：--TaskID（任务ID）、--files（文件路径，逗号分隔）\n'
     '  示例：cli_start.bat uploadParamfiles --TaskID LaWan00000001 --files ./data/model.stp,./data/params.csv'),
    ('newTaskverify',
     '校验任务参数文件完整性\n'
     '  参数：--TaskID（任务ID）\n'
     '  示例：cli_start.bat newTaskverify --TaskID LaWan00000001'),
    ('startTask',
     '启动仿真任务\n'
     '  参数：--TaskID（任务ID）\n'
     '  示例：cli_start.bat startTask --TaskID LaWan00000001'),
    ('queryTaskStatus',
     '查询任务当前状态\n'
     '  参数：--TaskID（任务ID）\n'
     '  示例：cli_start.bat queryTaskStatus --TaskID LaWan00000001'),
    ('stopTask',
     '停止正在运行的仿真任务\n'
     '  参数：--TaskID（任务ID）\n'
     '  示例：cli_start.bat stopTask --TaskID LaWan00000001'),
    ('deleteTask',
     '删除指定仿真任务\n'
     '  参数：--TaskID（任务ID）\n'
     '  示例：cli_start.bat deleteTask --TaskID LaWan00000001'),
    ('fetchTaskResult',
     '下载仿真任务结果文件\n'
     '  参数：--TaskID（任务ID）、--output（本地保存路径）\n'
     '  示例：cli_start.bat fetchTaskResult --TaskID LaWan00000001 --output ./result.zip'),
    ('help',
     '显示所有命令帮助信息\n'
     '  示例：cli_start.bat help'),
]


@click.command('help')
def aid_help() -> None:
    """显示 AID Client SDK 所有可用命令的说明。"""
    click.echo("=" * 60)
    click.echo("AID Client SDK 命令行工具帮助文档")
    click.echo("金属加工仿真系统客户端 SDK v1.0.0")
    click.echo("=" * 60)
    click.echo()

    for cmd_name, description in COMMANDS_HELP:
        click.echo(f"【{cmd_name}】")
        click.echo(f"  {description}")
        click.echo()

    click.echo("通用选项：")
    click.echo("  --config  指定配置文件路径（默认：./config/config.yml）")
    click.echo()
    click.echo("注意：所有命令均会将结果以 JSON 格式输出到标准输出。")


def main() -> None:
    """CLI 入口函数。"""
    aid_help()


if __name__ == '__main__':
    main()
