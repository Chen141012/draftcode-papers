# Agent 提示词模式速查

> 比赛时直接用的 Agent 提词模板。不研究理论，只给能直接抄的提词结构和实用模式。

## 来源
- Amazon Bedrock Agent Samples: https://github.com/awslabs/amazon-bedrock-agent-samples
- AWS Bedrock Agents 最佳实践: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-best-practices.html

## 1. 基础 Agent 提词结构

### 系统提示词模板
```
你是一个 NBA 选秀分析 Agent。你的职责是：

[角色定义]
你是数据驱动的选秀预测专家，基于 26 年历史 NBA 选秀数据进行分析。

[核心能力]
1. 数据分析 — 使用 Python 工具处理选秀数据，计算统计指标
2. 选秀预测 — 基于历史模式预测球队选秀选择
3. 可视化 — 生成图表展示分析结果

[行为规则]
- 每次分析前先检查数据质量
- 对不确定的预测明确标注置信度
- 用数据支撑每一个结论
- 结果以可视化表格展示

[输出格式]
- 预测结果：球员名 → 顺位 → 置信度 → 理由
- 可视化：交互式图表
```

### Tool Use + Action Group 结构
```python
# Agent 工具定义示例
tools = [
    {
        "name": "analyze_draft_data",
        "description": "分析选秀数据并返回统计指标",
        "parameters": {
            "year_range": {"type": "array", "items": {"type": "integer"}, "description": "年份范围 [起始, 结束]"},
            "metrics": {"type": "array", "items": {"type": "string"}, "description": "需要计算的指标列表"}
        }
    },
    {
        "name": "predict_pick",
        "description": "预测某支球队在指定顺位的选秀选择",
        "parameters": {
            "team": {"type": "string", "description": "球队名称"},
            "pick_number": {"type": "integer", "description": "选秀顺位"},
            "available_players": {"type": "array", "items": {"type": "string"}, "description": "可选球员列表"}
        }
    }
]
```

## 2. 结构化提词（Few-shot）

### 预测推理链
```
分析步骤：
1. 球队需求分析：查看球队阵容缺口
2. 历史模式匹配：球队在类似顺位的历史选择模式
3. 球员价值评估：可用球员的大学数据/体测数据
4. 综合判断：结合上述因素输出预测

示例：
球队：圣安东尼奥马刺
顺位：#4

Step 1 - 需求分析：
马刺当前阵容缺乏首发级别控卫（Tre Jones 为替补级别）
Step 2 - 历史模式：
马刺在乐透区偏好大学经验丰富的球员（3+年大学经历）
Step 3 - 球员评估：
[球员A] — 控卫，大四，PER 25.3，三分命中率 40.2%
[球员B] — 侧翼，大一，PER 22.1，三分命中率 33.5%
Step 4 - 预测：
选择球员A — 匹配历史模式 + 满足阵容需求
```

## 3. 实用提示

### 数据处理提词
```
你已获得 NBA 选秀历史数据集（格式：CSV）。
请执行以下步骤：
1. 使用 pandas 加载数据（工具：execute_python）
2. 检测缺失值并报告
3. 对关键特征进行统计分析
4. 输出数据摘要报告
```

### 可视化提词
```
基于分析结果，使用 plotly 生成交互式可视化：
1. 预测概率分布图（柱状图）
2. 球队-球员匹配热度图
3. 历史趋势对比折线图
```
