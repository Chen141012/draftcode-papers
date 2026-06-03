# Multi-Agent Collaboration Mechanisms: A Survey of LLMs

> **论文链接**: https://arxiv.org/abs/2501.06322
> **发表**: arXiv, Jan 2025
> **作者**: Khanh-Tung Tran et al.

## 为什么选这篇

比赛三样交付物之一"Web Agent 界面"需要 Agent 能力。这篇不是讲模型架构的，而是讲 **多 Agent 怎么协作**——直接对应我们在比赛中要搭建的 Agent 系统的设计。

## 核心内容

### 协作机制五维框架

| 维度 | 说明 | 比赛中的应用 |
|------|------|-------------|
| **Actors**（参与者） | 参与的 Agent 角色 | 数据Agent / 分析Agent / 展示Agent 分工 |
| **Types**（协作类型） | 合作 / 竞争 / 竞合 | 合作模式：多个 Agent 协同完成预测 |
| **Structures**（结构） | P2P / 集中 / 分布式 | 集中式：Supervisor Agent 调度子 Agent |
| **Strategies**（策略） | 基于角色 / 基于模型 | 基于角色：各 Agent 专职（数据清洗、特征、预测、可视化） |
| **Protocols**（协议） | 通信与协调机制 | 通过 AgentCore Gateway 通信 |

### 三种协作模式

| 模式 | 描述 | 适用场景 |
|------|------|---------|
| **合作** | Agent 共享目标、分工协作 | 数据清洗→特征工程→预测→展示 流水线 |
| **竞争** | Agent 各自独立推理、投票裁决 | 多个预测模型投票得出最终选秀结果 |
| **竞合** | 合作与竞争混合 | 先合作处理数据，再竞争输出多组预测结果对比 |

### 实用价值

这篇论文给出了 **可直接抄的协作架构模板**：

```
Supervisor Agent（总控）
    ├── Data Agent（数据处理）
    ├── Analysis Agent（特征分析+模型）
    ├── Prediction Agent（选秀预测）
    └── Visualization Agent（可视化展示）
```

比赛日可以直接套用这个结构：Supervisor 接收用户输入，分派给不同子 Agent 处理，汇总结果。

## 关键链接

- PDF: https://arxiv.org/pdf/2501.06322
- 相关 GitHub (Multi-Agent Survey): https://github.com/MiuLab/MultiAgent-Survey
