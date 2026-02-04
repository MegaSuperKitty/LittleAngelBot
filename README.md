![LittleAngelBot Logo](docs/logo.png)

<div align="center">
  <h1>LittleAngelBot: A Personal Assistant Powered by Mobile QQ and Windows PC Collaboration</h1>
  <p>
    <img src="https://img.shields.io/badge/python-≥3.11-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-Apache--2.0-green" alt="License">
    <a href="./COMMUNICATION.md"><img src="https://img.shields.io/badge/WeChat-Group-C5EAB4?style=flat&logo=wechat&logoColor=white" alt="WeChat"></a>
  </p>
</div>

首个国产版 OpenClaw 跨端个人助手 Agent。面向 Windows 电脑设计，打通手机端 QQ 与 Windows 端能力，让用户通过自然语言实现跨端自动规划与执行任务的闭环。

## 时间线
- **2026-02-03** 🎉 小天使🪽智能体开源啦，欢迎使用!

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

<table align="center">
  <tr align="center">
    <th><p align="center">🔎 信息搜集与报告生成</p></th>
    <th><p align="center">⏰ 定时任务与自动化执行</p></th>
    <th><p align="center">🧩 Skills自动创建</p></th>
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

环境变量：
- `BRAVE_API_KEY`（可选）
- `ZHIPU_API_KEY`（可选）
- `DASHSCOPE_API_KEY`（可选）
- `BOTPY_APPID`（QQ 入口需要）
- `BOTPY_SECRET`（QQ 入口需要）
- `LITTLE_ANGEL_AGENT_WORKSPACE`（可选，agent的工作路径）

### 本地使用密钥

请在项目根目录创建 `local_secrets.yaml`，并填写密钥：

```yaml
ZHIPU_API_KEY: ""
DASHSCOPE_API_KEY: ""
BOTPY_APPID: ""
BOTPY_SECRET: ""
```

注意：QQ机器人的APPID和SECRET请前往腾讯QQ开放平台注册并创建机器人获得（https://q.qq.com/#/）

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

- 在 `skills/` 中添加或修改技能
- 在 `tools/` 中新增工具能力
- 通过统一的 Skills 机制进行个性化配置

## 许可证

Apache-2.0
