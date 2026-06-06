# DraftCode 备战仓库

> NBA × AWS DraftCode 24h 黑客松 — **纯技术向比赛**（数据处理+Agent构建+Web展示），跟篮球分析关系不大。

## 总览

比赛三样交付物：**Web Agent 界面 + GitHub 代码仓库 + 预测结果表单**
评分权重：代码质量30% + 路演30% + 选秀命中率40%

备战策略：**比赛前准备好全部厨具和菜（模板/脚手架/代码框架），比赛日只做微调。**

## 模块概览

| 模块 | 状态 | 文件数 | 内容 |
|------|------|--------|------|
| **A** — 选秀预测知识 | 🟡 Phase 2 | 3 | 模型模板 + 球员指标 + 特征工程 |
| **B** — Agent 构建 | ✅ Phase 1 | 8 | 模板/提词/技能注入/记忆恢复 |
| **C** — 数据工程 | ✅ Phase 1 | 4 | 流水线/处理器/架构/SDK |
| **D** — 比赛策略 | ⏸ Phase 3 | 0 | 待开始 |

## 目录结构

```
├── A-draft-prediction/
│   ├── A1-draft-models/          ← 选秀预测模型
│   │   ├── deep-research-draft-factors.md  (深度调研报告)
│   │   └── draft-prediction-model-template.md  (XGBoost训练模板)
│   ├── A2-player-metrics/        ← 球员评估指标
│   │   └── player-evaluation-metrics-reference.md
│   └── A3-feature-engineering/   ← 特征工程
│       └── draft-prediction-feature-engineering.md
├── B-agent-building/
│   ├── B1-agent-patterns/        ← 设计模式+脚手架
│   ├── B2-prompt-engineering/    ← 提词工程模板
│   └── B3-skill-injection/       ← 技能注入+运行时
├── C-data-engineering/           ← 数据工程全流程模板
├── D-competition-strategy/       ← 比赛策略（待开始）
├── HANDOVER.md                   ← 跨对话交接
├── competition-overview.md       ← 比赛全貌
└── daily-log/                    ← 每日推送日志
```

## 时间线

| 日期 | 事件 |
|------|------|
| **6/16** | 线上培训 — 解锁数据格式与工具 |
| **6/23 09:00** | 开赛 |
| **6/24 08:00** | 交卷 |
| **6/24 09:00** | 路演（6分钟/队） |

## 关键链接

- 比赛官网: https://builderx.csdn.net/draftcode
- 仓库: https://github.com/Chen141012/draftcode-papers
- 标准化SOP: Obsidian → DraftCode备赛操作SOP.md
