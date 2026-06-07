# 比赛日作战手册

> 📋 24 小时完整作战计划。所有零件（模板/代码/参考）的集成方案。
> 从 H+0（开赛）到 H+24（交卷），逐段安排。

---

## 总览：24h 分段计划

```
H+0  ─ H+2   数据就位 + 环境搭建
H+2  ─ H+6   数据清洗 + 特征工程（最耗时）
H+6  ─ H+10  模型训练 + 调参
H+10 ─ H+14  Agent 搭建 + 工具集成
H+14 ─ H+18  Web UI + 预测结果输出
H+18 ─ H+20  路演准备 + 排练
H+20 ─ H+22  最终检查 + 补漏
H+22 ─ H+24  交卷 + 休息备演
```

---

## Phase 1: H+0 ~ H+2 — 数据就位 + 环境搭建

### 目标
确认数据可用、AWS 环境可跑、基础管道通

### 操作清单

```
[ ] 拿到比赛数据集（格式确认：CSV/JSON/Parquet？）
[ ] AWS 凭证验证：aws sts get-caller-identity
[ ] 模型可用确认：bedrock converse hello world
[ ] SageMaker/EC2 实例配额确认
[ ] S3 桶创建：draftcode-raw / draftcode-cleaned / draftcode-models
[ ] git clone draftcode-papers 到本地
```

### 使用的零件
- 📄 C: bedrock-claude-sdk-quickstart.md → SDK 验证
- 📄 C: sagemaker-data-pipeline-template.md → SageMaker 环境

### 危机预案
| 问题 | 应对 |
|------|------|
| AWS 配额不够 | 切本地 Python + pandas（C: nba-draft-data-processing-reference.md） |
| 数据格式不符预期 | 先用 pandas 读前100行探索结构 |
| Bedrock 模型不可用 | 切 Claude API key（如果准备了）或换本地模型 |

---

## Phase 2: H+2 ~ H+6 — 数据清洗 + 特征工程 ⭐ 最耗时

### 目标
原始数据 → 干净的训练用特征矩阵

### 操作清单

```
[ ] 数据探索性分析（shape/columns/dtypes/missing/corr）
[ ] 缺失值处理（中位数填充 / 丢弃）
[ ] 异常值检测 + 裁剪
[ ] 分类变量编码（LabelEncoder / OneHot）
[ ] 特征生成（see A3-feature-engineering）
[ ] 训练/测试集划分
[ ] 数据质量报告导出
```

### 使用的零件
- 📄 C: nba-draft-data-processing-reference.md → DraftDataProcessor class
- 📄 A3: draft-prediction-feature-engineering.md → 特征框架 + create_advanced_features()
- 📄 A2: player-evaluation-metrics-reference.md → 指标公式

### 时间分配建议
```
数据探索与清洗：   2h  (H+2 ~ H+4)
特征工程：         2h  (H+4 ~ H+6)
```

---

## Phase 3: H+6 ~ H+10 — 模型训练 + 调参

### 目标
训练预测模型 → 评估 → 输出 30 队选秀结果

### 操作清单

```
[ ] 基线模型（RandomForest 不用调参，10 分钟出结果）
[ ] 主模型训练（XGBoost）
[ ] 超参调优（grid search on max_depth/learning_rate/n_estimators）
[ ] 特征重要性分析 → 剪枝
[ ] 30 队选秀预测输出
[ ] 模型保存
```

### 使用的零件
- 📄 A1: draft-prediction-model-template.md → run_draft_pipeline()
- 📄 A1: deep-research-draft-factors.md → 6条高置信度发现作为先验知识

### 训练策略
```python
# 分层策略
Tier 1: XGBoost 默认参数 → 快速评估（30min）
   ↓ 如果 MAE > 15
Tier 2: 网格搜索调参（2h）
   ↓ 如果时间不够
Tier 3: 用默认 XGBoost 结果 + 规则后处理修正（保底）
```

---

## Phase 4: H+10 ~ H+14 — Agent 搭建 + 工具集成

### 目标
Agent 能调用数据/模型/展示工具，端到端跑通

### 操作清单

```
[ ] 选择 Agent 框架（AgentCore CLI / FAST / Streamlit 三选一）
[ ] 定义 Action Group（数据查询 → 模型预测 → 结果展示）
[ ] 接入 Bedrock 模型
[ ] Tool Use：analyze_draft_data / predict_pick / visualize
[ ] Agent 记忆配置（session 保持上下文）
[ ] 错误处理 + 降级策略
```

### 框架选择决策树
```
React 经验足？ → FAST（全栈模板）
  否 ↓
主要展示数据？ → Streamlit + LangChain（最快出 MVP）
  否 ↓
需要复杂 Agent 逻辑？ → AgentCore CLI + Streamlit 前端
```

### 使用的零件
- 📄 B1: FAST-fullstack-template-reference.md
- 📄 B1: agentcore-cli-quickstart.md
- 📄 B1: streamlit-bedrock-langchain-template.md
- 📄 B2: fewshot-draft-prediction-templates.md
- 📄 B3: agent-toolchain-setup.md
- 📄 B3: agent-memory-error-recovery.md

---

## Phase 5: H+14 ~ H+18 — Web UI + 结果输出

### 目标
可访问的 Web 界面 + 30 队预测结果表 + 可视化

### 操作清单

```
[ ] Agent 前端部署（Streamlit Cloud / Amplify / EC2）
[ ] 30 队选秀结果可视化（表格 + 柱状图 + 置信度标注）
[ ] 关键球员对比界面
[ ] 交互式查询功能（"为什么预测 XX 队选 XX？"）
[ ] 预测结果表单填写（比赛要求的第三样交付物）
```

### 交付物 3 件套确认
| 交付物 | 状态 | 备注 |
|--------|------|------|
| Web Agent 界面 | ⬜ | 可访问、可交互、展示预测结果 |
| GitHub 代码仓库 | ✅ | 已有，持续更新 |
| 预测结果表单 | ⬜ | 30 队完整名单 + 里程碑事件答案 |

---

## Phase 6: H+18 ~ H+20 — 路演准备

### 目标
6 分钟路演排练 + 演示环境就绪

### 操作清单

```
[ ] 路演 PPT 定稿（模板见 roadshow-template.md）
[ ] 完整排练 1 次（计时）
[ ] 备选演示方案（录屏/截图，防止现场翻车）
[ ] 回答预演（可能的评委提问）
```

### 路演结构（6分钟）
```
0:00-0:30  开场（一句话你要什么）
0:30-1:30  核心挑战（26年数据 + 30队预测）
1:30-3:30  技术方案（数据→模型→Agent→UI）
3:30-5:00  现场演示（Web Agent 界面跑一遍）
5:00-5:30  预测亮点（最自信的 3 个预测）
5:30-6:00  收尾 + Q
```

---

## Phase 7: H+20 ~ H+22 — 最终检查

### 交付物检查清单

```
□ Web Agent 界面可公开访问
□ 所有功能在演示环境可正常工作
□ 备选录屏已准备
□ GitHub 仓库提交最终版
□ README 更新到最新
□ 预测结果表单已提交
□ 代码无敏感信息泄露（token/key）
```

### 常见掉坑点
```
□ 数据集路径硬编码了？→ 改成环境变量或 argparse
□ Agent tool call 超时没处理？→ 加 retry
□ 可视化加载太慢？→ 预计算 + 缓存
□ 路演时网络不通？→ 本地录屏
□ 代码评分工具拉不到最新版本？→ 确认 main 分支是最新的
```

---

## Phase 8: H+22 ~ H+24 — 交卷 + 休息备演

```
□ 三样交付物全部提交
□ 预测结果表单确认无误
□ 团队休息 + 补充能量
□ 路演前 final check
```

---

## 组件集成图

```
比赛数据 (06.23 09:00)
    │
    ▼
┌──────────────────────────────────────────┐
│  C-数据工程                               │
│  DraftDataProcessor + SageMaker Pipeline  │
│  → 清洗 → 特征 → 训练/测试划分              │
└────────────────┬─────────────────────────┘
                 │ 特征矩阵
                 ▼
┌──────────────────────────────────────────┐
│  A-选秀预测模型                            │
│  XGBoost → 30队预测 → 置信度 → 输出CSV    │
└────────────────┬─────────────────────────┘
                 │ 预测结果
                 ▼
┌──────────────────────────────────────────┐
│  B-Agent 构建                             │
│  Agent 接收查询 → Tool Use → 推理 → 响应    │
└────────────────┬─────────────────────────┘
                 │ JSON 响应
                 ▼
┌──────────────────────────────────────────┐
│  Web UI (FAST / Streamlit)                │
│  交互式预测展示 + 可视化 + 查询             │
└──────────────────────────────────────────┘
                 │
                 ▼
          三样交付物提交
```
