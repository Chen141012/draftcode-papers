# Agent 工具链与能力注入速查

> 比赛时给 Agent 装"技能"的参考。重点是 Tool/Action Group 怎么配，能力怎么注入。
> 不研究理论框架，只给可以直接用的实现参考。

## 相关资源

- **Bedrock Agent Samples Tool 示例**: https://github.com/awslabs/amazon-bedrock-agent-samples/tree/main/src/shared
- **Bedrock AgentCore Gateway**: https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore-gateway.html

## 1. Action Group（工具能力）

### Lambda 工具模板
```python
import json
import boto3
import pandas as pd
import numpy as np

def lambda_handler(event, context):
    # 解析 Agent 调用参数
    params = event.get("parameters", {})
    action = event.get("actionGroup")
    
    if action == "analyze-draft-data":
        result = analyze_draft(params)
    elif action == "predict-picks":
        result = predict_picks(params)
    elif action == "visualize-results":
        result = visualize(params)
    
    return {
        "actionGroup": action,
        "function": "execute",
        "response": {
            "data": json.dumps(result, default=str)
        }
    }

def analyze_draft(params):
    """选秀数据分析"""
    # 这里写数据分析逻辑
    # 输入：历史选秀数据 → 输出：统计报告
    pass

def predict_picks(params):
    """选秀预测"""
    # 预测模型推理
    pass
```

### Action Group Schema (OpenAPI)
```yaml
openapi: 3.0.0
info:
  title: Draft Analysis API
  version: 1.0.0
paths:
  /analyze:
    post:
      summary: 分析选秀数据
      parameters:
        - name: year_start
          in: query
          schema: { type: integer }
        - name: year_end
          in: query
          schema: { type: integer }
      responses:
        '200':
          description: 分析结果
  /predict:
    post:
      summary: 预测选秀顺位
      parameters:
        - name: team
          in: query
          schema: { type: string }
        - name: pick
          in: query
          schema: { type: integer }
      responses:
        '200':
          description: 预测结果
```

## 2. AgentCore Gateway 工具

如果使用 AgentCore，Gateway 工具是最推荐的方式：

```python
# Gateway 工具定义（Lambda 后端）
from bedrock_agentcore import GatewayClient

gateway_client = GatewayClient(gateway_url="https://your-gateway-url")

# 注册为 Agent 工具
tool = gateway_client.create_tool(
    name="analyze_draft",
    description="Analyze historical NBA draft data",
    parameters={
        "query": {
            "type": "string",
            "description": "Analysis query in natural language"
        }
    }
)
```

## 3. Code Interpreter 能力

AgentCore 内置的 Code Interpreter 可以直接执行 Python 代码进行数据分析：

```python
# Agent 中使用 Code Interpreter
from bedrock_agentcore.code_interpreter import CodeInterpreterTool

interpreter = CodeInterpreterTool()

# Agent 可以动态执行：
# - pandas 数据分析
# - numpy 统计计算
# - plotly 可视化
# - sklearn 简单模型训练
```

## 4. 关键集成模式

### 模式A：直接调用 Bedrock 模型
```
用户输入 → Streamlit UI → Bedrock Claude → 返回预测
最简单，适合 MVP
```

### 模式B：Agent + Tools
```
用户输入 → Agent (推理/规划) 
  → Tool: analyze_draft_data
  → Tool: predict_picks  
  → Tool: visualize_results
→ 结构化输出
```

### 模式C：AgentCore Runtime
```
用户输入 → Streamlit UI → Cognito Auth → AgentCore Runtime
  → Gateway Tools (Lambda)
  → Code Interpreter
  → Memory
→ 流式响应
最适合比赛，代码质量分高
```

## 5. 比赛日快速启动清单

- [ ] 创建 AWS 账号（如果还没有）
- [ ] `aws configure` 设置凭证
- [ ] 安装 AgentCore CLI: `pip install agentcore-cli`
- [ ] 创建项目: `agentcore create`
- [ ] 定义 Action Group / Gateway Tools
- [ ] 部署到 AgentCore Runtime
- [ ] 连接 Streamlit/FAST 前端
- [ ] 测试端到端流程
