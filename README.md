# LittleAngelBot

![LittleAngelBot Logo](docs/logo.png)

国产版 OpenClaw 跨端个人助手 Agent。面向 Windows 电脑设计，打通手机端 QQ 与 Windows 端能力，让用户通过自然语言实现跨端自动规划与执行任务的闭环。

## 核心亮点

- 跨端个人智能体：手机端 QQ ↔ Windows 电脑端协同
- 多智能体架构：可并行拆解与推进复杂任务
- 智能路由：根据任务难度选择 `ReAct` 或 `ReCAP`
- 上下文工程：压缩、卸载、文件系统能力，避免上下文过长
- 安全沙箱与异步执行：更稳定的长链路任务运行
- Skills 能力集成：统一机制，支持个性化配置与再开发
- 任务状态管理：支持多轮复杂任务的长链路自动化执行
- 执行稳定：先规划后行动
- 正在集成经验学习：越用越好

## 演示动图

![演示动图](docs/demo.gif)

## 能力概览

- 信息搜集与整理
- 报告生成与文档输出
- 定时任务与自动化执行
- 开发编程任务的跨端执行

## 适用场景

- 工作/学习资料快速搜集与结构化整理
- 报告、清单、摘要的自动生成
- 需要跨端协作的多步骤任务
- 个人开发与脚本化自动化

## 运行前准备

建议使用环境变量配置密钥与运行参数。

环境变量：
- `BRAVE_API_KEY`（可选）
- `ZHIPU_API_KEY`（可选）
- `DASHSCOPE_API_KEY`（可选）
- `BOTPY_APPID`（QQ 入口需要）
- `BOTPY_SECRET`（QQ 入口需要）
- `LITTLE_ANGEL_AGENT_WORKSPACE`（可选，`agent_workspace` 路径）

### 本地测试密钥（可选）

为了方便本地测试，可以在项目根目录创建 `local_secrets.yaml`：

```yaml
BRAVE_API_KEY: ""
ZHIPU_API_KEY: ""
DASHSCOPE_API_KEY: ""
BOTPY_APPID: ""
BOTPY_SECRET: ""
```

读取优先级：入口文件内的默认值 > 环境变量 > `local_secrets.yaml`。

## 运行

### CLI

```powershell
python entry_cli.py
```

### QQ 私聊

```powershell
python entry_qq.py
```

## 目录结构

- `entry_cli.py`：CLI 入口（本地调试）
- `entry_qq.py`：QQ 私聊入口
- `little_angel_bot.py`：机器人核心逻辑
- `tools/`：工具能力
- `skills/`：Skills 能力集成
- `agent_workspace/`：运行产物与中间文件（建议忽略提交）

## 开发与扩展

- 在 `skills/` 中添加或修改技能
- 在 `tools/` 中新增工具能力
- 通过统一的 Skills 机制进行个性化配置

## 许可证

Apache-2.0
