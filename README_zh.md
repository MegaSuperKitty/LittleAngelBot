![LittleAngelBot Logo](docs/logo.png)

<div align="center">
  <h1>LittleAngelBot：手机 QQ 与 Windows 协同的个人助手</h1>
  <p>
    <img src="https://img.shields.io/badge/python-%E2%89%A53.11-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
    <a href="./COMMUNICATION.md"><img src="https://img.shields.io/badge/WeChat-Group-C5EAB4?style=flat&logo=wechat&logoColor=white" alt="WeChat"></a>
  </p>
</div>

[English README](./README.md)

首个国产版 OpenClaw 跨端个人助手 Agent。面向 Windows 电脑设计，打通手机端 QQ 与 Windows 端能力，让用户通过自然语言实现跨端自动规划与执行任务的闭环。

## 时间线

- **2026-02-03** 🎉 小天使🐣智能体开源啦，欢迎使用!

## 核心亮点

- 跨端个人助手：手机 QQ ↔ Windows PC 协同
- 多智能体架构：支持复杂任务并行拆解与推进
- 智能路由：根据任务复杂度自动选择 `ReAct` 或 `ReCAP`
- 上下文工程：压缩、卸载与文件系统协同，降低上下文溢出风险
- 安全沙箱与异步执行：提升长链路任务执行稳定性
- Skills 集成机制：支持能力扩展与个性化配置
- 任务状态管理：支持复杂任务的多轮自动执行
- 执行策略清晰：先规划、再行动

## 演示动图

<table align="center">
  <tr align="center">
    <th><p align="center">🔎 信息检索与报告生成</p></th>
    <th><p align="center">⏰ 定时任务与自动化执行</p></th>
    <th><p align="center">🧩 Skills 自动生成</p></th>
    <th><p align="center">💻 编程与远程执行</p></th>
  </tr>
  <tr>
    <td align="center"><p align="center"><img src="docs/Report.gif" width="180" height="400"></p></td>
    <td align="center"><p align="center"><img src="docs/StayHydrated.gif" width="180" height="400"></p></td>
    <td align="center"><p align="center"><img src="docs/GenerateSkills.gif" width="180" height="400"></p></td>
    <td align="center"><p align="center"><img src="docs/Coding.gif" width="180" height="400"></p></td>
  </tr>
</table>

## 能力概览

- 信息检索与整理
- 报告与文档生成
- 定时任务与自动化执行
- 跨端开发与代码任务执行

## 适用场景

- 工作/学习资料的快速搜集与结构化整理
- 报告、清单、摘要等内容自动生成
- 需要跨端协作的多步骤任务
- 个人开发流程与脚本自动化

## 运行前准备

环境变量：

- `LLM_API_KEY`（必填，用于模型调用）
- `LLM_BASE_URL`（可选；默认值由 `LLM_PROVIDER` 决定）
- `LLM_MODEL`（可选；默认值由 `LLM_PROVIDER` 决定）
- `LLM_PROVIDER`（可选，`openai|dashscope|siliconflow|anthropic`，也可自动识别）
- `BRAVE_API_KEY`（可选，用于网页搜索）
- `ZHIPU_API_KEY`（可选，用于网页搜索）
- `BOTPY_APPID`（必填，QQ 入口需要）
- `BOTPY_SECRET`（必填，QQ 入口需要）
- `LITTLE_ANGEL_AGENT_WORKSPACE`（可选，Agent 工作目录）

### 本地密钥文件

请在项目根目录创建 `local_secrets.yaml`，并填写：

```yaml
LLM_API_KEY: ""
LLM_BASE_URL: ""
LLM_MODEL: ""
LLM_PROVIDER: ""
ZHIPU_API_KEY: ""
BOTPY_APPID: ""
BOTPY_SECRET: ""
```

说明：QQ 机器人的 `APPID` 与 `SECRET` 请在腾讯 QQ 开放平台注册并创建机器人后获取：https://q.qq.com/#/

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

- `entry_qq.py`：QQ 私聊入口
- `entry_cli.py`：CLI 入口
- `little_angel_bot.py`：机器人核心逻辑
- `tools/`：工具能力
- `skills/`：Skills 能力集成

## 开发与扩展

- 在 `skills/` 中新增或修改技能
- 在 `tools/` 中新增工具能力
- 通过统一 Skills 机制做个性化扩展

## 许可证

MIT
