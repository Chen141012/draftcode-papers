# FAST: Fullstack AgentCore Solution Template

> 直接抄作业的#1资源。AWS 官方全栈模板：React 前端 + AgentCore 后端 + Cognito 认证 + CDK 基础设施。
> 比赛日三样交付物之一"Web Agent 界面"可以直接基于此搭建。

## 仓库

- **GitHub**: https://github.com/awslabs/fullstack-solution-template-for-agentcore
- **Stars**: 1500+ | **Commits**: 566+ | **活跃度**: 极高（持续更新）
- **License**: Apache-2.0

## 能直接抄什么

| 比赛交付物 | FAST 对应 |
|-----------|-----------|
| Web Agent 界面 | React 前端（Tailwind CSS + shadcn/ui），开箱即用 |
| GitHub 代码仓库 | 完整的 CDK/Terraform 部署脚本 |
| 后端 Agent 逻辑 | AgentCore Runtime，框架无关（Strands/LangGraph 都行） |

## 技术栈

- **前端**: React + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **后端**: Amazon Bedrock AgentCore Runtime（框架无关）
- **认证**: Amazon Cognito
- **基础设施**: AWS CDK（也支持 Terraform）
- **部署**: AWS Amplify Hosting

## 启动步骤

```bash
# 1. Fork 仓库
git clone https://github.com/awslabs/fullstack-solution-template-for-agentcore.git
cd fullstack-solution-template-for-agentcore

# 2. 部署基础设施（一行命令）
cd infra-cdk
cdk deploy

# 3. 前端自动部署到 Amplify
# 详见 docs/DEPLOYMENT.md
```

## 内置功能

- **Gateway Tools**: Lambda 驱动的工具，带认证
- **Code Interpreter**: 直接集成 Bedrock AgentCore Code Interpreter
- **记忆系统**: AgentCore Memory 接入
- **流式响应**: Streaming HTTP 实时展示
- **多 Agent 协作**: 支持 Supervisor 模式

## 为什么选它

1. **比赛明确要求 Web Agent 界面** — FAST 提供现成的 React 前端
2. **评分 30% 代码质量** — FAST 遵循 AWS 安全最佳实践，代码组织专业
3. **24h 比赛时间紧张** — 部署好 FAST 基线系统只需要几行 CDK 命令，省去从头搭建基础设施
4. **框架无关** — 可以用 Strands、LangGraph、LangChain 等任意框架开发 Agent 逻辑
5. **Vibe-coding 友好** — 内置 AI coding assistant 上下文文档，可以直接用 Claude 改前端

## 关键文档索引

- `docs/DEPLOYMENT.md` — 部署指南
- `docs/AGENT_CONFIGURATION.md` — Agent 配置
- `docs/STREAMING.md` — 流式实现
- `docs/MEMORY_INTEGRATION.md` — 记忆集成
- `patterns/` — Agent 模式示例（Strands / LangGraph）

## 快速定制

替换 Agent 核心逻辑：修改 `patterns/strands-single-agent/basic_agent.py` 中的 system_prompt 和 tools。
前端显示：修改 `frontend/src/app/` 下的页面组件。
