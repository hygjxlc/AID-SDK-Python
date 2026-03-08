from setuptools import setup, find_packages

setup(
    name='aid-client-sdk',
    version='1.0.0',
    description='AID Client SDK - 金属加工仿真系统客户端SDK',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.8',
    install_requires=[
        'requests>=2.28.0',
        'pyyaml>=6.0',
        'click>=8.0.0',
        'python-json-logger>=2.0.0',
    ],
    entry_points={
        'console_scripts': [
            'aid-newTaskCreate=aid_sdk.cli.cmd_new_task_create:main',
            'aid-uploadParamfiles=aid_sdk.cli.cmd_upload_paramfiles:main',
            'aid-newTaskverify=aid_sdk.cli.cmd_new_task_verify:main',
            'aid-startTask=aid_sdk.cli.cmd_start_task:main',
            'aid-queryTaskStatus=aid_sdk.cli.cmd_query_task_status:main',
            'aid-stopTask=aid_sdk.cli.cmd_stop_task:main',
            'aid-deleteTask=aid_sdk.cli.cmd_delete_task:main',
            'aid-fetchTaskResult=aid_sdk.cli.cmd_fetch_task_result:main',
            'aid-help=aid_sdk.cli.cmd_help:main',
        ],
    },
)
