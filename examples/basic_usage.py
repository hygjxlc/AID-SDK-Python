"""
AID Client SDK Python 使用示例
=================================
本示例展示了使用 AID Client SDK 完成金属加工仿真任务的完整工作流程：
  1. 创建仿真任务
  2. 上传参数文件
  3. 校验文件完整性
  4. 启动任务
  5. 轮询查询任务状态
  6. 下载仿真结果

运行前请确保：
  - 已安装 SDK：pip install aid-client-sdk
  - 已在当前目录准备好 config.yml 配置文件
  - config.yml 中已填写正确的 baseURL 和 api_token
"""

import time
import os

# 导入 AID SDK 主类及异常
from aid_sdk import AidClient
from aid_sdk.common.exceptions import AidException as AidApiException


# ============================================================
# 配置项：根据实际情况修改以下参数
# ============================================================

# 配置文件路径（包含 baseURL 和 api_token）
CONFIG_PATH = "./config/config.yml"

# 仿真类型（可选值：LaWan / CHOnYA / ZhuZao / ZhaZhi / ZHEWan / JIYA）
SIMULATE_TYPE = "LaWan"

# 任务名称（自定义，便于识别）
TASK_NAME = "python_demo_task_001"

# 需要上传的参数文件路径列表（文件名须在服务端白名单中）
# 白名单必需文件: config.yml, feature_line_ref_0.stp, feature_line_ref_1.stp,
#               left_boundary.txt, materials.csv, mould_section.stp, strip_section.stp
# 白名单可选文件: product.stp, mesh.jnl, support_side_mould_x.stp 等
PARAM_FILES = [
    "./data/product.stp",              # 可选：三维模型文件
    "./data/materials.csv",            # 必需：材料参数文件
    "./data/config.yml",               # 必需：配置文件
    "./data/feature_line_ref_0.stp",   # 必需：特征线参考文件0
    "./data/feature_line_ref_1.stp",   # 必需：特征线参考文件1
    "./data/left_boundary.txt",        # 必需：左边界条件
    "./data/mould_section.stp",        # 必需：模具截面
    "./data/strip_section.stp",        # 必需：料带截面
]

# 仿真结果下载目录
OUTPUT_DIR = "./results/"

# 状态轮询间隔（秒）
POLL_INTERVAL = 10


def main():
    """主函数：执行完整仿真流程"""

    print("=" * 50)
    print("AID Client SDK Python 使用示例")
    print(f"仿真类型: {SIMULATE_TYPE}")
    print(f"任务名称: {TASK_NAME}")
    print("=" * 50)

    # --------------------------------------------------
    # 步骤 0：初始化 AidClient
    # --------------------------------------------------
    # AidClient 会自动读取配置文件中的 baseURL 和 api_token
    # 后续所有 API 调用均通过此客户端实例发起
    print("\n[初始化] 加载配置文件并创建 AidClient...")
    client = AidClient(config_path=CONFIG_PATH)
    print("AidClient 初始化成功")

    task_id = None  # 用于保存任务 ID，供后续步骤使用

    try:
        # --------------------------------------------------
        # 步骤 1：创建仿真任务
        # --------------------------------------------------
        print(f"\n[步骤 1/6] 创建仿真任务...")
        create_resp = client.new_task_create(
            simulate_type=SIMULATE_TYPE,
            task_name=TASK_NAME
        )

        # 检查响应码，200 表示成功
        if create_resp.code != 200:
            raise RuntimeError(f"创建任务失败 [code={create_resp.code}]: {create_resp.message}")

        # 保存任务 ID，后续所有操作均需要它
        task_id = create_resp.data.task_id if create_resp.data else None
        print(f"✓ 任务创建成功，TaskID: {task_id}")

        # --------------------------------------------------
        # 步骤 2：上传参数文件
        # --------------------------------------------------
        print(f"\n[步骤 2/6] 上传参数文件...")
        print(f"待上传文件: {PARAM_FILES}")

        upload_resp = client.upload_param_files(
            task_id=task_id,
            file_paths=PARAM_FILES
        )

        if upload_resp.code != 200:
            raise RuntimeError(f"文件上传失败 [code={upload_resp.code}]: {upload_resp.message}")

        # 打印服务端已接收到的文件列表
        file_list = upload_resp.data.file_list if upload_resp.data else []
        print(f"✓ 文件上传成功，已上传文件: {file_list}")

        # --------------------------------------------------
        # 步骤 3：校验文件完整性
        # --------------------------------------------------
        # 服务端会检查任务所需的必要文件是否已全部上传
        print(f"\n[步骤 3/6] 校验文件完整性...")
        verify_resp = client.new_task_verify(task_id=task_id)

        if verify_resp.code != 200:
            raise RuntimeError(f"文件校验请求失败 [code={verify_resp.code}]: {verify_resp.message}")

        # ready=False 说明仍有文件未上传
        if verify_resp.data and not verify_resp.data.ready:
            missing_files = verify_resp.data.left_file_list if verify_resp.data else []
            print(f"✗ 文件校验未通过，以下文件仍需上传:")
            for f in missing_files:
                print(f"   - {f}")
            raise RuntimeError("文件不完整，请补充上传后重试")

        print("✓ 文件校验通过，任务已就绪，可以启动")

        # --------------------------------------------------
        # 步骤 4：启动仿真任务
        # --------------------------------------------------
        print(f"\n[步骤 4/6] 启动仿真任务...")
        start_resp = client.start_task(task_id=task_id)

        if start_resp.code != 200:
            raise RuntimeError(f"启动任务失败 [code={start_resp.code}]: {start_resp.message}")

        status = start_resp.data.status if start_resp.data else "UNKNOWN"
        print(f"✓ 任务启动成功，当前状态: {status}")

        # --------------------------------------------------
        # 步骤 5：轮询查询任务状态
        # --------------------------------------------------
        print(f"\n[步骤 5/6] 等待任务完成（每 {POLL_INTERVAL} 秒查询一次）...")

        while True:
            # 查询当前任务状态
            status_resp = client.query_task_status(task_id=task_id)

            if status_resp.code != 200:
                print(f"  警告：查询状态失败 [code={status_resp.code}]，继续等待...")
                time.sleep(POLL_INTERVAL)
                continue

            status = status_resp.data.status if status_resp.data else "UNKNOWN"

            # 提取进度信息（如果有的话）
            extra_info = status_resp.data.extra_info if status_resp.data else {}
            progress = extra_info.get("progress", "N/A") if isinstance(extra_info, dict) else "N/A"
            current_step = extra_info.get("currentStep", "") if isinstance(extra_info, dict) else ""

            # 打印当前进度
            progress_str = f"进度: {progress}%" if progress != "N/A" else ""
            step_str = f"当前步骤: {current_step}" if current_step else ""
            info_parts = [s for s in [progress_str, step_str] if s]
            info_str = f" | {' | '.join(info_parts)}" if info_parts else ""
            print(f"  状态: {status}{info_str}")

            # 任务完成，退出轮询
            if status == "COMPLETED":
                print("✓ 任务计算完成！")
                break

            # 任务异常结束（失败或被停止）
            elif status == "FAILED":
                raise RuntimeError(f"仿真任务执行失败，请查看任务日志排查原因")

            elif status == "STOPPED":
                raise RuntimeError(f"仿真任务已被停止")

            # 任务仍在运行，等待后继续轮询
            time.sleep(POLL_INTERVAL)

        # --------------------------------------------------
        # 步骤 6：下载仿真结果
        # --------------------------------------------------
        print(f"\n[步骤 6/6] 下载仿真结果...")

        # 确保输出目录存在
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        result_resp = client.fetch_task_result(
            task_id=task_id,
            output_path=OUTPUT_DIR
        )

        if result_resp.code != 200:
            raise RuntimeError(f"下载结果失败 [code={result_resp.code}]: {result_resp.message}")

        result_path = result_resp.data.result_file_path if result_resp.data else OUTPUT_DIR
        print(f"✓ 仿真结果已下载至: {result_path}")

    except AidApiException as e:
        # 处理 SDK 抛出的 API 错误（带有错误码）
        print(f"\n✗ API 错误 [code={e.error_code}]: {e.error_message}")
        _print_error_hint(e.error_code)

    except RuntimeError as e:
        # 处理流程中的业务错误
        print(f"\n✗ 流程错误: {e}")

    except ConnectionError as e:
        # 处理网络连接错误
        print(f"\n✗ 网络连接失败: {e}")
        print("  请检查 config.yml 中的 baseURL 是否正确，以及网络是否可达")

    except Exception as e:
        # 处理其他未预期的异常
        print(f"\n✗ 未知异常: {type(e).__name__}: {e}")

    finally:
        # 如果需要清理（如失败时删除任务），可在此处添加
        print("\n" + "=" * 50)
        print("示例执行结束")
        if task_id:
            print(f"任务 ID: {task_id}")
        print("=" * 50)


def _print_error_hint(error_code: int):
    """根据错误码打印处理建议"""
    hints = {
        301: "  提示：TaskID 不存在，请确认任务 ID 是否正确",
        302: "  提示：当前任务状态不允许此操作，请检查任务流程",
        303: "  提示：文件格式不支持或超出大小限制（stp/txt/csv/yml/jnl，单文件≤100MB，总量≤500MB）",
        401: "  提示：API Key 无效，请检查 config.yml 中的 api_token 配置",
        402: "  提示：请求参数有误，请检查传入参数是否正确",
        403: "  提示：权限不足，请联系管理员确认账号权限",
        500: "  提示：服务器内部错误，请联系 AID 技术支持",
    }
    hint = hints.get(error_code, "  提示：请参阅 API 文档或联系技术支持")
    print(hint)


if __name__ == "__main__":
    main()
