# DraftCode 备战 — 交接文档

> 给新对话的快速上下文，读完后去看 SOP 和对应目录。

## 一句话

帮朋友调研 NBA×AWS DraftCode 24h 黑客松（6/23-24 上海世博中心）。
比赛纯技术向（跟篮球关系不大），核心是数据处理+Agent构建+Web展示。

## 当前完整状态（截至 6/10）

| 模块 | 文件 | 内容 | 状态 |
|------|------|------|------|
| **A** 选秀预测 | 5 | 调研报告+XGBoost模板+训练pipeline.py+指标参考+特征工程 | 🟡 |
| **B** Agent构建 | 9 | 4模板+2提词+2运行时+agent_app.py(CLI) | ✅ |
| **C** 数据工程 | 7 | 4参考+data_processor.py+Bedrock SDK+mock数据生成 | ✅ |
| **D** 比赛策略 | 2 | 24h作战手册+路演模板 | 🟡 |
| **Web UI** | 1 | app.py(Streamlit, 交付物#1) | 🟢 新增 |
| **项目配置** | 1 | requirements.txt | 🟢 |
| **daily-log** | 8 | 6/2-6/10 | 🟢 |

**代码行数**: 3 .py + requirements.txt + app.py = ~600+ 行 Python
**总文件**: 25+

## 关键日期

- **6/16** 线上培训 — 解锁数据格式与工具（最重要的里程碑）
- **6/18** 报名截止
- **6/23 09:00** 开赛
- **6/24 08:00** 交卷
- **6/24 09:00** 路演

## 代码集成关系

```
generate_mock_data.py (or real data on 6/16)
    ↓ CSV
data_processor.py: load → preprocess → X, y
    ↓ 特征矩阵
draft_pipeline.py: train → evaluate → predict → model.json
    ↓ 预测结果
agent_app.py / app.py (Streamlit UI) → Web Agent 界面
```

## 新对话快速启动

```bash
# 1. 读 SOP
Read Obsidian: DraftCode备赛操作SOP.md

# 2. 读最新日志
Read GitHub: daily-log/2026-06-09.md

# 3. 了解代码结构
Read GitHub: data_processor.py (前30行)
Read GitHub: draft_pipeline.py (前30行)
Read GitHub: agent_app.py (前30行)
Read GitHub: app.py (前30行)
```

## 工作节奏

- Chen 主导节奏
- 所有产出先讨论再执行（铁律3）
- Token 在 SOP 笔记硬编码
