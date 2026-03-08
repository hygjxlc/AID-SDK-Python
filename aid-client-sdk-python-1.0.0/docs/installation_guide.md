# AID Client SDK（Python 版）安装与配置手册

## 目录

1. [环境要求](#1-环境要求)
2. [目录结构](#2-目录结构)
3. [安装步骤](#3-安装步骤)
4. [配置文件说明](#4-配置文件说明)
5. [日志配置](#5-日志配置)
6. [运行示例](#6-运行示例)
7. [完整调用示例](#7-完整调用示例)
8. [常见问题](#8-常见问题)

---

## 1. 环境要求

| 组件 | 版本要求 | 说明 |
|-----|---------|------|
| Python | 3.9+ | 运行时环境 |
| pip | 最新版 | 依赖管理 |
| 操作系统 | Windows 10+ / Linux / macOS | 均支持 |

### 验证环境

```bash
python --version
# 期望输出：Python 3.9.x 或更高

pip --version
# 期望输出：pip xx.x ...
```

---

## 2. 目录结构

```
aid-client-sdk-python/
├── config/
│   └── config.yml                # SDK 配置文件（重要）
├── examples/
│   └── basic_usage.py            # 使用示例（参考）
├── src/aid_sdk/                  # SDK 源码包
│   ├── auth/                     # 认证模块
│   ├── cli/                      # 命令行工具
│   ├── common/                   # 公共模块（异常、响应等）
│   ├── config/                   # 配置加载模块
│   ├── http/                     # HTTP 客户端
│   ├── logging/
│   │   └── aid_logger.py         # 日志配置模块（重要）
│   ├── task/                     # 任务管理模块
│   └── client.py                 # AidClient 主入口
├── tests/                        # 测试用例
├── logs/                         # 日志目录（运行时自动创建）
│   └── aid-sdk.log
├── requirements.txt              # 依赖列表
├── requirements-dev.txt          # 开发依赖列表
└── setup.py                      # 安装配置
```

---

## 3. 安装步骤

### 3.1 克隆代码

```bash
git clone <仓库地址>
cd aid-client-sdk-python
```

### 3.2 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖包：

| 包名 | 版本 | 用途 |
|-----|-----|------|
| requests | >=2.28.0 | HTTP 请求 |
| pyyaml | >=6.0 | 配置文件解析（YAML 格式） |
| click | >=8.0.0 | 命令行工具支持 |
| python-json-logger | >=2.0.0 | JSON 格式日志输出 |

### 3.3 安装 SDK 本身（可选）

如需在其他项目中以包形式引用：

```bash
pip install -e .
```

---

## 4. 配置文件说明

配置文件路径：`config/config.yml`

```yaml
# AID Client SDK Configuration
baseURL: "http://127.0.0.1:8080/api/v1"
api_token: "11111111"
```

### 4.1 字段说明

| 字段 | 说明 | 示例 |
|-----|------|------|
| `baseURL` | AID-Service 服务地址，包含协议、IP、端口和路径前缀 | `http://127.0.0.1:8080/api/v1` |
| `api_token` | 认证密钥，须与服务端配置一致 | `11111111` |

### 4.2 常见配置场景

**本机调试（默认）：**
```yaml
baseURL: "http://127.0.0.1:8080/api/v1"
api_token: "11111111"
```

**连接远程服务器：**
```yaml
baseURL: "http://192.168.1.100:8080/api/v1"
api_token: "your_production_api_key"
```

> **重要**：URL 路径必须以 `/api/v1` 结尾，不能使用旧版路径 `/aid-service`。

### 4.3 指定配置文件路径

`AidClient` 初始化时可传入自定义配置文件路径：

```python
from aid_sdk import AidClient

# 默认路径：./config/config.yml
client = AidClient(config_path="./config/config.yml")

# 自定义路径
client = AidClient(config_path="/etc/aid/config.yml")
```

---

## 5. 日志配置

日志模块：`src/aid_sdk/logging/aid_logger.py`

### 5.1 日志级别修改

找到以下代码行修改日志级别：

```python
# src/aid_sdk/logging/aid_logger.py

logger.setLevel(logging.DEBUG)   # 修改此处
```

| 级别常量 | 适用场景 |
|---------|---------|
| `logging.DEBUG` | 开发、测试阶段，输出详细调试信息 |
| `logging.INFO` | 生产环境，记录关键流程（推荐） |
| `logging.WARNING` | 只记录警告及以上 |
| `logging.ERROR` | 只记录错误 |

修改后**无需重新安装**，直接重新运行即可生效。

### 5.2 日志文件位置

- 日志目录：`logs/`（相对于脚本运行目录，自动创建）
- 当前日志：`logs/aid-sdk.log`
- 历史日志：`logs/aid-sdk.log.YYYY-MM-DD`（按天滚动，保留 30 天）

### 5.3 日志输出方式

同时输出到**控制台**和**文件**，格式均为 JSON：

```json
{"asctime": "2026-03-05T14:10:48", "levelname": "INFO", "name": "aid_sdk.task.task_service", "message": "创建任务成功", "api": "new_task_create", "taskID": "AID-20260305-001"}
```

### 5.4 日志滚动策略

| 配置 | 值 |
|-----|-----|
| 滚动时间 | 每天午夜（midnight） |
| 保留天数 | 30 天 |
| 编码 | UTF-8 |

---

## 6. 运行示例

### 6.1 运行完整示例

```bash
cd aid-client-sdk-python

# 运行示例（需先启动 AID-Service 服务端）
python examples/basic_usage.py
```

### 6.2 使用 CLI 命令行工具

```bash
# 查看帮助
python -m aid_sdk.cli.main help

# 创建任务
python -m aid_sdk.cli.main new-task-create --type LaWan --name my_task --config ./config/config.yml

# 上传参数文件
python -m aid_sdk.cli.main upload-paramfiles --task-id <taskId> --files ./data/model.stp ./data/params.csv

# 校验文件
python -m aid_sdk.cli.main new-task-verify --task-id <taskId>

# 启动任务
python -m aid_sdk.cli.main start-task --task-id <taskId>

# 查询状态
python -m aid_sdk.cli.main query-task-status --task-id <taskId>

# 停止任务
python -m aid_sdk.cli.main stop-task --task-id <taskId>

# 删除任务
python -m aid_sdk.cli.main delete-task --task-id <taskId>

# 下载结果
python -m aid_sdk.cli.main fetch-task-result --task-id <taskId> --output ./results/
```

---

## 7. 完整调用示例

参考 `examples/basic_usage.py`，完整流程如下：

```
初始化 AidClient（读取 config.yml）
    ↓
步骤 1：new_task_create（创建仿真任务）→ 获取 TaskID
    ↓
步骤 2：upload_param_files（上传参数文件）
    ↓
步骤 3：new_task_verify（校验文件完整性）
    ↓
步骤 4：start_task（启动任务）
    ↓
步骤 5：query_task_status（轮询状态，每 10 秒一次）
    ↓ 状态 = COMPLETED
步骤 6：fetch_task_result（下载仿真结果）
```

### 关键配置常量（basic_usage.py）

| 常量 | 说明 | 默认值 |
|-----|------|-------|
| `CONFIG_PATH` | 配置文件路径 | `./config.yml` |
| `SIMULATE_TYPE` | 仿真类型 | `LaWan` |
| `TASK_NAME` | 任务名称 | `python_demo_task_001` |
| `PARAM_FILES` | 参数文件路径列表 | `./data/model.stp` 等 |
| `OUTPUT_DIR` | 结果下载目录 | `./results/` |
| `POLL_INTERVAL` | 状态轮询间隔（秒） | `10` |

### 支持的仿真类型

| 值 | 说明 |
|----|------|
| `LaWan` | 拉弯成型 |
| `CHOnYA` | 冲压 |
| `ZhuZao` | 铸造 |
| `ZhaZhi` | 轧制 |
| `ZHEWan` | 折弯 |
| `JIYA` | 挤压 |

### 响应对象访问方式

SDK 返回的响应为对象（非字典），使用 `.` 属性访问：

```python
resp = client.new_task_create("LaWan", "my_task")

# 正确：属性访问
resp.code          # 响应码
resp.message       # 响应消息
resp.data.task_id  # 任务 ID

# 错误：字典访问（会报 TypeError）
resp["code"]       # ❌ 不支持
```

---

## 8. 常见问题

### Q1：`ModuleNotFoundError: No module named 'aid_sdk'`

**原因**：SDK 包未安装，或未在正确目录运行。

**解决方案一**：在项目根目录运行：
```bash
cd aid-client-sdk-python
python examples/basic_usage.py
```

**解决方案二**：以开发模式安装：
```bash
pip install -e .
```

---

### Q2：API 返回 401 认证失败

**错误**：`API Key认证失败，无效的密钥`

**原因**：`config.yml` 中的 `api_token` 与服务端不一致。

**解决**：检查并对齐：
- SDK：`config/config.yml` → `api_token`
- 服务端：`AID-service/app_config.yaml` → `auth.api_key`

---

### Q3：API 返回 404 Not Found

**原因**：`baseURL` 路径配置错误，使用了旧版 `/aid-service` 路径。

**解决**：
```yaml
# 正确
baseURL: "http://127.0.0.1:8080/api/v1"

# 错误（旧版）
baseURL: "http://127.0.0.1:8080/aid-service"
```

---

### Q4：`TypeError: 'AidResponse' object is not subscriptable`

**原因**：使用了字典方式访问响应对象（`resp["code"]`），SDK 响应为对象类型。

**解决**：改为属性访问：
```python
# 错误
if resp["code"] != 200:
    task_id = resp["taskID"]

# 正确
if resp.code != 200:
    task_id = resp.data.task_id
```

---

### Q5：连接超时 / 服务无法访问

**原因**：AID-Service 未启动，或 `baseURL` 地址有误。

**解决步骤**：
1. 确认 AID-Service 已启动并监听 8080 端口
2. 验证服务是否正常：
   ```bash
   curl http://127.0.0.1:8080/api/v1/health
   ```
3. 检查 `config.yml` 中的 `baseURL` 是否正确

---

### Q6：`ImportError: No module named 'pythonjsonlogger'`

**原因**：`python-json-logger` 未安装。

**解决**：
```bash
pip install python-json-logger>=2.0.0
```

---

### Q7：日志文件没有生成

**原因**：`logs/` 目录会在第一次调用日志时自动创建，若脚本运行路径不固定，日志可能生成在意外位置。

**解决**：日志文件生成在**脚本运行时的当前工作目录**下的 `logs/` 文件夹中。建议固定工作目录运行：
```bash
cd aid-client-sdk-python
python examples/basic_usage.py
```

日志将生成于：`aid-client-sdk-python/logs/aid-sdk.log`
