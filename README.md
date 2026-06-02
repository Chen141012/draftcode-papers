# DraftCode Papers

> NBA × AWS DraftCode 24h 黑客松 — 选秀预测 Agent 论文研读计划

## 备战体系

```
模块 A：选秀预测 ────────── 核心知识（什么因素影响选秀结果）
├─ A1 历史选秀规律 + 市场效率
│   · 机器学习/统计模型预测选秀顺位
│   · 博彩/赔率市场视角（从市场经济学的角度理解选秀）
│   · mock draft 聚合与评估
├─ A2 球员价值评估指标
│   · PER / BPM / RAPTOR / LEBRON / EPM 等方法论
│   · 各类指标的信度与效度
└─ A3 特征工程
    · 哪些大学/体测数据最能预测 NBA 成功
    · 数据维度的取舍与组合

模块 B：Agent 构建 ──────── 提词 + 工具链
├─ B1 Agent 设计模式
│   · Chain-of-Thought / 多Agent协作 / Tool Use
├─ B2 Prompt 工程
│   · 结构化提词、Few-shot、元技能注入
└─ B3 经验与技能注入
    · Agent 自我改进、失败模式编码

模块 C：数据工程 ────────── 拿到数据怎么用
├─ C1 数据集理解（26年选秀数据长什么样）
├─ C2 AWS 工具链（Bedrock / SageMaker）
└─ C3 数据清洗与特征建构

模块 D：比赛策略 ────────── 实战
├─ D1 交付物规划（Web Agent 界面设计）
├─ D2 24小时时间管理
└─ D3 路演准备（6分钟讲什么）
```

## 目录结构

```
draftcode-papers/
├── README.md                   ← 本文件
├── A-draft-prediction/         ← 模块A：选秀预测
│   ├── A1-draft-models/        ← 选秀预测模型 + 市场效率
│   ├── A2-player-metrics/      ← 球员价值评估指标
│   └── A3-feature-engineering/ ← 特征工程
├── B-agent-building/           ← 模块B：Agent 构建
│   ├── B1-agent-patterns/
│   ├── B2-prompt-engineering/
│   └── B3-skill-injection/
├── C-data-engineering/         ← 模块C：数据工程
├── D-competition-strategy/     ← 模块D：比赛策略
└── daily-log/                  ← 每日推送日志

