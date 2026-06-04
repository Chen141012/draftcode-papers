# Amazon Bedrock + Claude SDK 速查

> 比赛日直接用的 Bedrock API 调用示例。两种方式：boto3 (InvokeModel/Converse) 和 Anthropic SDK。

## 核心模型 ID

| 模型 | 全局 ID (推荐) | 区域 ID |
|------|---------------|---------|
| Claude Sonnet 4.6 | `us.anthropic.claude-sonnet-4-6` | `anthropic.claude-sonnet-4-6` |
| Claude Opus 4.6 | `us.anthropic.claude-opus-4-6-v1` | `anthropic.claude-opus-4-6-v1` |
| Claude Haiku 4.5 | `us.anthropic.claude-haiku-4-5` | `anthropic.claude-haiku-4-5` |

> 全局 ID（`us.` 前缀）推荐：路由到最优区域，吞吐更高，成本约低 10%。

## 方式一：Boto3 InvokeModel（基础）

```python
import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

response = bedrock.invoke_model(
    modelId="us.anthropic.claude-sonnet-4-6",
    contentType="application/json",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "system": "你是一个 NBA 选秀分析专家。",
        "messages": [
            {"role": "user", "content": "分析这个选秀数据：[...]"}
        ]
    })
)

result = json.loads(response["body"].read())
print(result["content"][0]["text"])
```

## 方式二：Boto3 Converse API（推荐）

> Converse API 更简洁，不需要拼 JSON body，结构化输出更方便。

```python
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

response = bedrock.converse(
    modelId="us.anthropic.claude-sonnet-4-6",
    system=[{"text": "你是一个 NBA 选秀预测专家。按 JSON 格式输出预测结果。"}],
    messages=[
        {"role": "user", "content": [{"text": "预测马刺队#4顺位的选择"}]}
    ],
    inferenceConfig={
        "maxTokens": 4096,
        "temperature": 0.3,
        "topP": 0.9
    }
)

print(response["output"]["message"]["content"][0]["text"])
```

## 方式三：Anthropic Bedrock SDK（最简洁）

```bash
pip install anthropic
```

```python
from anthropic import AnthropicBedrock

client = AnthropicBedrock(aws_region="us-east-1")

message = client.messages.create(
    model="us.anthropic.claude-sonnet-4-6",
    max_tokens=4096,
    temperature=0.3,
    system="你是 NBA 选秀预测 Agent。",
    messages=[
        {"role": "user", "content": "预测勇士队#14顺位的选择"}
    ]
)

print(message.content[0].text)
```

## 流式响应

```python
with client.messages.stream(
    model="us.anthropic.claude-sonnet-4-6",
    max_tokens=4096,
    messages=[{"role": "user", "content": "逐步分析30支球队选秀"}]
) as stream:
    for chunk in stream:
        if chunk.type == "content_block_delta":
            print(chunk.delta.text, end="", flush=True)
```

## Tool Use（函数调用）

```python
import json

response = bedrock.converse(
    modelId="us.anthropic.claude-sonnet-4-6",
    messages=[{"role": "user", "content": [{"text": "分析2024年选秀数据"}]}],
    toolConfig={
        "tools": [
            {
                "toolSpec": {
                    "name": "analyze_draft",
                    "description": "分析选秀数据",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "year": {"type": "integer", "description": "年份"},
                                "metrics": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "required": ["year"]
                        }
                    }
                }
            }
        ]
    }
)

# 处理 Tool Use
content = response["output"]["message"]["content"]
for block in content:
    if "toolUse" in block:
        tool_name = block["toolUse"]["name"]
        tool_input = block["toolUse"]["input"]
        print(f"Agent 调用了: {tool_name}({json.dumps(tool_input)})")
        # 执行工具并返回结果
```

## 模型选择建议

| 任务 | 推荐模型 | 理由 |
|------|---------|------|
| 数据分析（大量上下文） | Sonnet 4.6 | 性价比最高，200K上下文 |
| 复杂推理（多步骤） | Opus 4.6 | 推理能力最强 |
| 简单格式化/分类 | Haiku 4.5 | 速度快，成本低 |
| 流式展示给用户 | Sonnet 4.6 | 响应快，质量好 |

## 比赛日 Quickstart

```bash
# 1. 确认凭证
aws sts get-caller-identity

# 2. 确认模型可用
aws bedrock list-foundation-models --region us-east-1 | grep claude

# 3. 最小可用测试
python3 -c "
import boto3, json
c = boto3.client('bedrock-runtime', region_name='us-east-1')
r = c.converse(modelId='us.anthropic.claude-sonnet-4-6', messages=[{'role':'user','content':[{'text':'hello'}]}])
print(r['output']['message']['content'][0]['text'])
"
```
