#!/bin/bash
# AID Client SDK CLI 启动脚本
# 使用方法: ./cli_start.sh <命令> [参数]

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检测是否已通过 pip 安装 aid-client-sdk（whl 模式）
if python -c "import aid_sdk" >/dev/null 2>&1; then
    # whl 已安装，无需设置 PYTHONPATH
    export PYTHONPATH=""
else
    # 未安装，回退到 src/ 目录模式
    export PYTHONPATH="${SCRIPT_DIR}/src"
fi

# 显示帮助信息
show_help() {
    echo "============================================================"
    echo "AID Client SDK CLI 启动脚本"
    echo "============================================================"
    echo ""
    echo "用法: ./cli_start.sh <命令> [参数]"
    echo ""
    echo "可用命令:"
    echo "  help              显示帮助信息"
    echo "  newTaskCreate     创建新任务"
    echo "  uploadParamfiles  上传参数文件"
    echo "  newTaskverify     校验任务文件"
    echo "  startTask         启动任务"
    echo "  queryTaskStatus   查询任务状态"
    echo "  stopTask          停止任务"
    echo "  deleteTask        删除任务"
    echo "  fetchTaskResult   获取任务结果"
    echo ""
    echo "============================================================"
    echo "命令详细示例"
    echo "============================================================"
    echo ""
    echo "[1] help - 显示帮助信息"
    echo "  ./cli_start.sh help"
    echo ""
    echo "[2] newTaskCreate - 创建新任务"
    echo "  ./cli_start.sh newTaskCreate --simulateType LaWan --taskName myTask001"
    echo "  参数说明:"
    echo "    --simulateType  仿真类型: LaWan / CHOnYA / ZhuZao / ZhaZhi / ZHEWan / JIYA"
    echo "    --taskName      任务名称: 自定义字符串"
    echo ""
    echo "[3] uploadParamfiles - 上传参数文件"
    echo "  ./cli_start.sh uploadParamfiles --TaskID LaWan00000001 --files ./examples/data/model.stp ./examples/data/params.csv"
    echo "  参数说明:"
    echo "    --TaskID  任务ID: 如 LaWan00000001"
    echo "    --files   文件路径: 多个文件用空格或逗号分隔"
    echo ""
    echo "[4] newTaskverify - 校验任务文件"
    echo "  ./cli_start.sh newTaskverify --TaskID LaWan00000001"
    echo "  参数说明:"
    echo "    --TaskID  任务ID: 如 LaWan00000001"
    echo ""
    echo "[5] startTask - 启动任务"
    echo "  ./cli_start.sh startTask --TaskID LaWan00000001"
    echo "  参数说明:"
    echo "    --TaskID  任务ID: 如 LaWan00000001"
    echo ""
    echo "[6] queryTaskStatus - 查询任务状态"
    echo "  ./cli_start.sh queryTaskStatus --TaskID LaWan00000001"
    echo "  参数说明:"
    echo "    --TaskID  任务ID: 如 LaWan00000001"
    echo ""
    echo "[7] stopTask - 停止任务"
    echo "  ./cli_start.sh stopTask --TaskID LaWan00000001"
    echo "  参数说明:"
    echo "    --TaskID  任务ID: 如 LaWan00000001"
    echo ""
    echo "[8] deleteTask - 删除任务"
    echo "  ./cli_start.sh deleteTask --TaskID LaWan00000001"
    echo "  参数说明:"
    echo "    --TaskID  任务ID: 如 LaWan00000001"
    echo ""
    echo "[9] fetchTaskResult - 获取任务结果"
    echo "  ./cli_start.sh fetchTaskResult --TaskID LaWan00000001 --output ./examples/data/result"
    echo "  参数说明:"
    echo "    --TaskID  任务ID: 如 LaWan00000001"
    echo "    --output  输出目录路径: 如 ./examples/data/result"
    echo ""
    echo "============================================================"
}

# 检查参数
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

# 获取命令并移除第一个参数
CMD="$1"
shift

# 构建剩余参数数组
ARGS=()
while [ $# -gt 0 ]; do
    ARGS+=("$1")
    shift
done

# 如果用户未指定 --config，自动使用根目录的 config.yml
if ! printf '%s\n' "${ARGS[@]}" | grep -q -- '--config'; then
    ARGS+=("--config" "config/config.yml")
fi

show_error_example() {
    local cmd="$1"
    echo ""
    echo "[错误] 命令执行失败，请检查参数是否正确"
    echo ""
    echo "正确示例:"
    case "$cmd" in
        newTaskCreate)
            echo "  ./cli_start.sh newTaskCreate --simulateType LaWan --taskName myTask001"
            echo ""
            echo "参数说明:"
            echo "  --simulateType  仿真类型: LaWan / CHOnYA / ZhuZao / ZhaZhi / ZHEWan / JIYA"
            echo "  --taskName      任务名称: 自定义字符串"
            ;;
        uploadParamfiles)
            echo "  ./cli_start.sh uploadParamfiles --TaskID LaWan00000001 --files ./examples/data/model.stp ./examples/data/params.csv"
            echo ""
            echo "参数说明:"
            echo "  --TaskID  任务ID: 如 LaWan00000001"
            echo "  --files   文件路径: 多个文件用空格或逗号分隔"
            ;;
        newTaskverify)
            echo "  ./cli_start.sh newTaskverify --TaskID LaWan00000001"
            echo ""
            echo "参数说明:"
            echo "  --TaskID  任务ID: 如 LaWan00000001"
            ;;
        startTask)
            echo "  ./cli_start.sh startTask --TaskID LaWan00000001"
            echo ""
            echo "参数说明:"
            echo "  --TaskID  任务ID: 如 LaWan00000001"
            ;;
        queryTaskStatus)
            echo "  ./cli_start.sh queryTaskStatus --TaskID LaWan00000001"
            echo ""
            echo "参数说明:"
            echo "  --TaskID  任务ID: 如 LaWan00000001"
            ;;
        stopTask)
            echo "  ./cli_start.sh stopTask --TaskID LaWan00000001"
            echo ""
            echo "参数说明:"
            echo "  --TaskID  任务ID: 如 LaWan00000001"
            ;;
        deleteTask)
            echo "  ./cli_start.sh deleteTask --TaskID LaWan00000001"
            echo ""
            echo "参数说明:"
            echo "  --TaskID  任务ID: 如 LaWan00000001"
            ;;
        fetchTaskResult)
            echo "  ./cli_start.sh fetchTaskResult --TaskID LaWan00000001 --output ./examples/data/result"
            echo ""
            echo "参数说明:"
            echo "  --TaskID  任务ID: 如 LaWan00000001"
            echo "  --output  输出目录路径: 如 ./examples/data/result"
            ;;
    esac
}

EXIT_CODE=0

case "$CMD" in
    help)
        python -m aid_sdk.cli.cmd_help "${ARGS[@]}"
        EXIT_CODE=$?
        ;;
    newTaskCreate)
        python -m aid_sdk.cli.cmd_new_task_create "${ARGS[@]}"
        EXIT_CODE=$?
        if [ $EXIT_CODE -ne 0 ]; then
            show_error_example "newTaskCreate"
        fi
        ;;
    uploadParamfiles)
        # 把 --files 后面空格分隔的多个文件路径合并为逗号分隔的单个值
        UPLOAD_ARGS=$(python "$SCRIPT_DIR/examples/_merge_files_args.py" -- "${ARGS[@]}")
        python -m aid_sdk.cli.cmd_upload_paramfiles $UPLOAD_ARGS
        EXIT_CODE=$?
        if [ $EXIT_CODE -ne 0 ]; then
            show_error_example "uploadParamfiles"
        fi
        ;;
    newTaskverify)
        python -m aid_sdk.cli.cmd_new_task_verify "${ARGS[@]}"
        EXIT_CODE=$?
        if [ $EXIT_CODE -ne 0 ]; then
            show_error_example "newTaskverify"
        fi
        ;;
    startTask)
        python -m aid_sdk.cli.cmd_start_task "${ARGS[@]}"
        EXIT_CODE=$?
        if [ $EXIT_CODE -ne 0 ]; then
            show_error_example "startTask"
        fi
        ;;
    queryTaskStatus)
        python -m aid_sdk.cli.cmd_query_task_status "${ARGS[@]}"
        EXIT_CODE=$?
        if [ $EXIT_CODE -ne 0 ]; then
            show_error_example "queryTaskStatus"
        fi
        ;;
    stopTask)
        python -m aid_sdk.cli.cmd_stop_task "${ARGS[@]}"
        EXIT_CODE=$?
        if [ $EXIT_CODE -ne 0 ]; then
            show_error_example "stopTask"
        fi
        ;;
    deleteTask)
        python -m aid_sdk.cli.cmd_delete_task "${ARGS[@]}"
        EXIT_CODE=$?
        if [ $EXIT_CODE -ne 0 ]; then
            show_error_example "deleteTask"
        fi
        ;;
    fetchTaskResult)
        python -m aid_sdk.cli.cmd_fetch_task_result "${ARGS[@]}"
        EXIT_CODE=$?
        if [ $EXIT_CODE -ne 0 ]; then
            show_error_example "fetchTaskResult"
        fi
        ;;
    *)
        echo "错误: 未知命令 '$CMD'"
        echo "运行 './cli_start.sh' 查看可用命令"
        EXIT_CODE=1
        ;;
esac

exit $EXIT_CODE
