# AID Client SDK（Python 版）用户手册

## 目录

1. [环境要求](#1-环境要求)
2. [安装包内容](#2-安装包内容)
3. [快速开始](#3-快速开始)
4. [配置文件说明](#4-配置文件说明)
5. [CLI 命令使用](#5-cli-命令使用)
6. [完整工作流程](#6-完整工作流程)
7. [日志说明](#7-日志说明)
8. [常见问题](#8-常见问题)

---

## 1. 环境要求

| 组件 | 版本要求 | 说明 |
|-----|---------|------|
| Python | 3.9+ | 运行时环境 |
| pip | 最新版 | 依赖和 SDK 安装工具 |
| 操作系统 | Windows 10+ / Linux / macOS | 均支持 |

### 验证环境

```bash
python --version
# 期望输出：Python 3.9.x 或更高

pip --version
# 期望输出：pip xx.x ...
```

---

## 2. 安装包内容

解压 `aid-client-sdk-python-1.0.0.zip` 后目录如下：

```
aid-client-sdk-python/
├── aid_client_sdk-1.0.0-py3-none-any.whl  ← SDK 安装包（pip 安装）
├── config/
│   └── config.yml                          ← 服务器地址和认证配置（必须修改）
├── cli_start.bat                           ← Windows CLI 启动脚本
├── cli_start.sh                            ← Linux/macOS CLI 启动脚本
├── examples/
│   ├── basic_usage.py                      ← Python 调用示例
│   └── data/                               ← 示例数据文件
├── docs/
│   └── installation_guide.md              ← 本手册
└── requirements.txt                        ← 依赖列表
```

---

## 3. 快速开始

### 3.1 安装依赖

```bash
python -m pip install -r requirements.txt
```

### 3.2 安装 SDK

```bash
python -m pip install aid_client_sdk-1.0.0-py3-none-any.whl
```

验证安装成功：

```bash
python -c "import aid_sdk; print('SDK 安装成功')"
```

### 3.3 修改配置文件

编辑 `config/config.yml`，填写服务器地址和认证密钥（详见 [第 4 章](#4-配置文件说明)）。

### 3.4 运行 CLI

```bash
# Windows（从 SDK 根目录运行，不带参数查看帮助）
cli_start.bat

# Linux / macOS
./cli_start.sh
```

---

## 4. 配置文件说明

配置文件路径：`config/config.yml`

```yaml
# AID Client SDK Configuration
baseURL: "http://111.228.12.67:28090/api/v1"
api_token: "11111111"
```

### 4.1 字段说明

| 字段 | 说明 | 示例 |
|-----|------|------|
| `baseURL` | AID-Service 服务地址，包含协议、IP、端口和路径前缀 | `http://111.228.12.67:28090/api/v1` |
| `api_token` | 认证密钥，须与服务端配置一致 | `11111111` |

> **重要**：URL 路径必须以 `/api/v1` 结尾。

### 4.2 连接其他服务器

```yaml
baseURL: "http://192.168.1.100:8080/api/v1"
api_token: "your_api_key"
```

---

## 5. CLI 命令使用

`cli_start.bat`（Windows）/ `cli_start.sh`（Linux/macOS）封装了所有命令，**默认自动使用 `config/config.yml`**，无需每次手动指定。

### 5.1 查看帮助

```bash
# 不带参数运行，显示所有命令和示例
cli_start.bat
```

### 5.2 各命令说明

#### 1. 创建任务 — `newTaskCreate`

```bash
cli_start.bat newTaskCreate --simulateType LaWan --taskName myTask001
```

| 参数 | 说明 | 可选值 |
|-----|------|-------|
| `--simulateType` | 仿真类型 | `LaWan` / `CHOnYA` / `ZhuZao` / `ZhaZhi` / `ZHEWan` / `JIYA` |
| `--taskName` | 任务名称 | 自定义字符串 |

**返回**：任务 ID，如 `LaWan00000001`

---

#### 2. 上传参数文件 — `uploadParamfiles`

```bash
# 方式一：逗号分隔（推荐）
cli_start.bat uploadParamfiles --TaskID LaWan00000001 --files ./examples/data/model.stp,./examples/data/params.csv

# 方式二：空格分隔（脚本自动转换）
cli_start.bat uploadParamfiles --TaskID LaWan00000001 --files ./examples/data/model.stp ./examples/data/params.csv
```

| 参数 | 说明 |
|-----|------|
| `--TaskID` | 任务 ID |
| `--files` | 文件路径，多个文件用逗号或空格分隔 |

---

#### 3. 校验文件 — `newTaskverify`

```bash
cli_start.bat newTaskverify --TaskID LaWan00000001
```

---

#### 4. 启动任务 — `startTask`

```bash
cli_start.bat startTask --TaskID LaWan00000001
```

---

#### 5. 查询任务状态 — `queryTaskStatus`

```bash
cli_start.bat queryTaskStatus --TaskID LaWan00000001
```

**返回状态值：**

| 状态 | 说明 |
|-----|------|
| `pending` | 等待中 |
| `running` | 仿真进行中 |
| `completed` | 完成，可下载结果 |
| `failed` | 失败 |
| `stopped` | 已停止 |

---

#### 6. 停止任务 — `stopTask`

```bash
cli_start.bat stopTask --TaskID LaWan00000001
```

---

#### 7. 删除任务 — `deleteTask`

```bash
cli_start.bat deleteTask --TaskID LaWan00000001
```

---

#### 8. 获取任务结果 — `fetchTaskResult`

```bash
cli_start.bat fetchTaskResult --TaskID LaWan00000001 --output ./result.zip
```

| 参数 | 说明 |
|-----|------|
| `--TaskID` | 任务 ID |
| `--output` | 结果文件保存路径，如 `./result.zip` |

> **注意**：任务状态为 `completed` 后才能下载结果。

---

#### 9. 指定配置文件 — `--config`

若需使用非默认配置文件：

```bash
cli_start.bat newTaskCreate --simulateType LaWan --taskName test --config ./my_config.yml
```

---

## 6. 完整工作流程

典型的仿真任务从创建到获取结果，完整流程如下：

```
步骤 1  newTaskCreate    → 创建任务，获得 TaskID
   ↓
步骤 2  uploadParamfiles → 上传仿真所需的参数文件
   ↓
步骤 3  newTaskverify    → 校验文件完整性（服务端验证）
   ↓
步骤 4  startTask        → 启动仿真任务
   ↓
步骤 5  queryTaskStatus  → 轮询状态，直到 completed
   ↓
步骤 6  fetchTaskResult  → 下载仿真结果文件
```

### 完整示例脚本（Windows）

```bat
@echo off
set TASK_ID=

REM 1. 创建任务
cli_start.bat newTaskCreate --simulateType LaWan --taskName demo_task

REM 2. 上传参数文件（将 LaWan00000001 替换为实际返回的 TaskID）
cli_start.bat uploadParamfiles --TaskID LaWan00000001 --files ./examples/data/model.stp,./examples/data/params.csv

REM 3. 校验文件
cli_start.bat newTaskverify --TaskID LaWan00000001

REM 4. 启动任务
cli_start.bat startTask --TaskID LaWan00000001

REM 5. 查询状态（手动多次执行直到 completed）
cli_start.bat queryTaskStatus --TaskID LaWan00000001

REM 6. 下载结果
cli_start.bat fetchTaskResult --TaskID LaWan00000001 --output ./result.zip
```

### 支持的仿真类型

| 值 | 说明 |
|----|------|
| `LaWan` | 拉弯成型 |
| `CHOnYA` | 冲压 |
| `ZhuZao` | 铸造 |
| `ZhaZhi` | 轧制 |
| `ZHEWan` | 折弯 |
| `JIYA` | 挤压 |

---

## 7. 日志说明

SDK 运行时自动在**当前工作目录**下创建 `logs/` 目录：

- 当前日志：`logs/aid-sdk.log`
- 历史日志：`logs/aid-sdk.log.YYYY-MM-DD`（按天滚动，保留 30 天）

日志格式为 JSON，同时输出到控制台和文件：

```json
{"asctime": "2026-03-05T14:10:48", "levelname": "INFO", "message": "创建任务成功", "taskID": "LaWan00000001"}
```




### Q4：`fetchTaskResult` 提示任务未完成

**原因**：任务仍在运行中，尚未达到 `completed` 状态。

**解决**：先用 `queryTaskStatus` 确认状态为 `completed` 再下载。

---

### Q5：上传多个文件只上传了第一个

**原因**：多个文件之间使用了错误的分隔方式。

**解决**：使用逗号分隔或空格分隔均可：
```bash
# 逗号分隔
--files ./model.stp,./params.csv

# 空格分隔（cli_start 脚本自动处理）
--files ./model.stp ./params.csv
```

---

### Q6：`ImportError: No module named 'pythonjsonlogger'`

**解决**：
```bash
pip install python-json-logger>=2.0.0
```

或重新安装所有依赖：
```bash
pip install -r requirements.txt
```
