# AgentCore CLI 快速上手

> 最快的 Agent 项目搭建方式。一条命令创建完整项目框架。
> 适合比赛日快速搭建 Agent 脚手架。

## 来源

- **GitHub**: https://github.com/aws/agentcore-cli
- **Samples**: https://github.com/awslabs/agentcore-samples (570+ commits)
- **文档**: https://docs.aws.amazon.com/bedrock-agentcore/

## 安装与创建项目

```bash
# 前提：aws configure + uv
pip install agentcore-cli

# 创建新项目（交互式向导）
agentcore create

# 选择框架：Strands Agents / LangGraph / CrewAI / OpenAI / Google ADK
# 选择语言：Python / TypeScript
# 项目自动生成，包含完整的 Dockerfile、requirements.txt、测试
```

## 本地开发

```bash
cd your-project
agentcore develop  # 启动本地开发服务器，自动热重载
```

## 部署到 AWS

```bash
agentcore launch  # 一键部署到 Bedrock AgentCore Runtime
```

## Samples 仓库结构

| 目录 | 内容 |
|------|------|
| `00-getting-started/` | 第一个 Agent（CLI 快速上手） |
| `01-features/` | AgentCore 功能深度示例（Gateway / Memory / Code Interpreter 等） |
| `02-end-to-end/` | 完整应用（可直接借鉴架构） |
| `03-integrations/` | 连接外部系统（第三方 IdP / 可观测性 / 数据平台） |
| `04-infrastructure-as-code/` | CDK / CloudFormation / Terraform 部署模板 |
| `05-blueprints/` | 全栈参考应用 |

## 比赛实用场景

1. **比赛日早上 9:00** → `agentcore create` 创建项目
2. **编写 Agent 逻辑**（数据处理 + 预测）→ 本地 `agentcore develop`
3. **部署到 AWS** → `agentcore launch`
4. **搭配 Streamlit/FAST 前端** → 连上 Runtime 端点

## 关键链接

- AgentCore CLI 文档: https://github.com/aws/agentcore-cli
- AgentCore SDK (Python): https://github.com/aws/bedrock-agentcore-sdk-python
- AgentCore SDK (TypeScript): https://github.com/aws/bedrock-agentcore-sdk-typescript
- 示例集合: https://github.com/awslabs/agentcore-samples
