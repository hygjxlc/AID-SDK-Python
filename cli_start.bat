@echo off
chcp 65001 >nul
REM AID Client SDK CLI 启动脚本
REM 使用方法: cli_start.bat <命令> [参数]

setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"

REM 检测是否已通过 pip 安装 aid-client-sdk（whl 模式）
python -c "import aid_sdk" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    REM whl 已安装，无需设置 PYTHONPATH
    set "PYTHONPATH="
) else (
    REM 未安装，回退到 src/ 目录模式
    set "PYTHONPATH=%SCRIPT_DIR%src"
)

if "%~1"=="" (
    echo ============================================================
    echo AID Client SDK CLI 启动脚本
    echo ============================================================
    echo.
    echo 用法: cli_start.bat ^<命令^> [参数]
    echo.
    echo 可用命令:
    echo   help              显示帮助信息
    echo   newTaskCreate     创建新任务
    echo   uploadParamfiles  上传参数文件
    echo   newTaskverify     校验任务文件
    echo   startTask         启动任务
    echo   queryTaskStatus   查询任务状态
    echo   stopTask          停止任务
    echo   deleteTask        删除任务
    echo   fetchTaskResult   获取任务结果
    echo.
    echo ============================================================
    echo 命令详细示例
    echo ============================================================
    echo.
    echo [1] help - 显示帮助信息
    echo   cli_start.bat help
    echo.
    echo [2] newTaskCreate - 创建新任务
    echo   cli_start.bat newTaskCreate --simulateType LaWan --taskName myTask001
    echo   参数说明:
    echo     --simulateType  仿真类型: LaWan / CHOnYA / ZhuZao / ZhaZhi / ZHEWan / JIYA
    echo     --taskName      任务名称: 自定义字符串
    echo.
    echo [3] uploadParamfiles - 上传参数文件
    echo   cli_start.bat uploadParamfiles --TaskID LaWan00000001 --files .\examples\data\model.stp .\examples\data\params.csv
    echo   参数说明:
    echo     --TaskID  任务ID: 如 LaWan00000001
    echo     --files   文件路径: 多个文件用空格或逗号分隔
    echo.
    echo [4] newTaskverify - 校验任务文件
    echo   cli_start.bat newTaskverify --TaskID LaWan00000001
    echo   参数说明:
    echo     --TaskID  任务ID: 如 LaWan00000001
    echo.
    echo [5] startTask - 启动任务
    echo   cli_start.bat startTask --TaskID LaWan00000001
    echo   参数说明:
    echo     --TaskID  任务ID: 如 LaWan00000001
    echo.
    echo [6] queryTaskStatus - 查询任务状态
    echo   cli_start.bat queryTaskStatus --TaskID LaWan00000001
    echo   参数说明:
    echo     --TaskID  任务ID: 如 LaWan00000001
    echo.
    echo [7] stopTask - 停止任务
    echo   cli_start.bat stopTask --TaskID LaWan00000001
    echo   参数说明:
    echo     --TaskID  任务ID: 如 LaWan00000001
    echo.
    echo [8] deleteTask - 删除任务
    echo   cli_start.bat deleteTask --TaskID LaWan00000001
    echo   参数说明:
    echo     --TaskID  任务ID: 如 LaWan00000001
    echo.
    echo [9] fetchTaskResult - 获取任务结果
    echo   cli_start.bat fetchTaskResult --TaskID LaWan00000001 --output .\examples\data\result
    echo   参数说明:
    echo     --TaskID  任务ID: 如 LaWan00000001
    echo     --output  输出目录路径: 如 .\examples\data\result
    echo.
    echo ============================================================
    goto :eof
)

set "CMD=%~1"

REM 构建参数列表（跳过第一个参数）
set "ARGS="
shift
:loop
if "%~1"=="" goto :done
set "ARGS=!ARGS! %~1"
shift
goto :loop
:done

set "EXIT_CODE=0"

REM 如果用户未指定 --config，自动使用根目录的 config.yml
echo !ARGS! | findstr /C:"--config" >nul 2>&1
if errorlevel 1 (
    set "ARGS=!ARGS! --config config\config.yml"
)

if "%CMD%"=="help" (
    python -m aid_sdk.cli.cmd_help !ARGS!
    set "EXIT_CODE=!ERRORLEVEL!"
) else if "%CMD%"=="newTaskCreate" (
    python -m aid_sdk.cli.cmd_new_task_create !ARGS!
    set "EXIT_CODE=!ERRORLEVEL!"
    if !EXIT_CODE! neq 0 (
        echo.
        echo [错误] 命令执行失败，请检查参数是否正确
        echo.
        echo 正确示例:
        echo   cli_start.bat newTaskCreate --simulateType LaWan --taskName myTask001
        echo.
        echo 参数说明:
        echo   --simulateType  仿真类型: LaWan / CHOnYA / ZhuZao / ZhaZhi / ZHEWan / JIYA
        echo   --taskName      任务名称: 自定义字符串
    )
) else if "%CMD%"=="uploadParamfiles" (
    REM 把 --files 后面空格分隔的多个文件路径合并为逗号分隔的单个值
    python "%SCRIPT_DIR%examples\_merge_files_args.py" -- !ARGS! > "%TEMP%\upload_args.tmp"
    set /p UPLOAD_ARGS=<"%TEMP%\upload_args.tmp"
    python -m aid_sdk.cli.cmd_upload_paramfiles !UPLOAD_ARGS!
    set "EXIT_CODE=!ERRORLEVEL!"
    if !EXIT_CODE! neq 0 (
        echo.
        echo [错误] 命令执行失败，请检查参数是否正确
        echo.
        echo 正确示例:
        echo   cli_start.bat uploadParamfiles --TaskID LaWan00000001 --files .\examples\data\model.stp .\examples\data\params.csv
        echo   cli_start.bat uploadParamfiles --TaskID LaWan00000001 --files .\examples\data\model.stp,.\examples\data\params.csv
        echo.
        echo 参数说明:
        echo   --TaskID  任务ID: 如 LaWan00000001
        echo   --files   文件路径: 多个文件用空格或逗号分隔
    )
) else if "%CMD%"=="newTaskverify" (
    python -m aid_sdk.cli.cmd_new_task_verify !ARGS!
    set "EXIT_CODE=!ERRORLEVEL!"
    if !EXIT_CODE! neq 0 (
        echo.
        echo [错误] 命令执行失败，请检查参数是否正确
        echo.
        echo 正确示例:
        echo   cli_start.bat newTaskverify --TaskID LaWan00000001
        echo.
        echo 参数说明:
        echo   --TaskID  任务ID: 如 LaWan00000001
    )
) else if "%CMD%"=="startTask" (
    python -m aid_sdk.cli.cmd_start_task !ARGS!
    set "EXIT_CODE=!ERRORLEVEL!"
    if !EXIT_CODE! neq 0 (
        echo.
        echo [错误] 命令执行失败，请检查参数是否正确
        echo.
        echo 正确示例:
        echo   cli_start.bat startTask --TaskID LaWan00000001
        echo.
        echo 参数说明:
        echo   --TaskID  任务ID: 如 LaWan00000001
    )
) else if "%CMD%"=="queryTaskStatus" (
    python -m aid_sdk.cli.cmd_query_task_status !ARGS!
    set "EXIT_CODE=!ERRORLEVEL!"
    if !EXIT_CODE! neq 0 (
        echo.
        echo [错误] 命令执行失败，请检查参数是否正确
        echo.
        echo 正确示例:
        echo   cli_start.bat queryTaskStatus --TaskID LaWan00000001
        echo.
        echo 参数说明:
        echo   --TaskID  任务ID: 如 LaWan00000001
    )
) else if "%CMD%"=="stopTask" (
    python -m aid_sdk.cli.cmd_stop_task !ARGS!
    set "EXIT_CODE=!ERRORLEVEL!"
    if !EXIT_CODE! neq 0 (
        echo.
        echo [错误] 命令执行失败，请检查参数是否正确
        echo.
        echo 正确示例:
        echo   cli_start.bat stopTask --TaskID LaWan00000001
        echo.
        echo 参数说明:
        echo   --TaskID  任务ID: 如 LaWan00000001
    )
) else if "%CMD%"=="deleteTask" (
    python -m aid_sdk.cli.cmd_delete_task !ARGS!
    set "EXIT_CODE=!ERRORLEVEL!"
    if !EXIT_CODE! neq 0 (
        echo.
        echo [错误] 命令执行失败，请检查参数是否正确
        echo.
        echo 正确示例:
        echo   cli_start.bat deleteTask --TaskID LaWan00000001
        echo.
        echo 参数说明:
        echo   --TaskID  任务ID: 如 LaWan00000001
    )
) else if "%CMD%"=="fetchTaskResult" (
    python -m aid_sdk.cli.cmd_fetch_task_result !ARGS!
    set "EXIT_CODE=!ERRORLEVEL!"
    if !EXIT_CODE! neq 0 (
        echo.
        echo [错误] 命令执行失败，请检查参数是否正确
        echo.
        echo 正确示例:
        echo   cli_start.bat fetchTaskResult --TaskID LaWan00000001 --output .\examples\data\result
        echo.
        echo 参数说明:
        echo   --TaskID  任务ID: 如 LaWan00000001
        echo   --output  输出目录路径: 如 .\examples\data\result
    )
) else (
    echo 错误: 未知命令 '%CMD%'
    echo 运行 'cli_start.bat' 查看可用命令
    set "EXIT_CODE=1"
)

endlocal
exit /b %EXIT_CODE%
