# Agent 记忆管理与错误恢复

> Agent 运行时的"保命"机制：状态持久化、对话历史管理、异常恢复。
> 比赛 24 小时持续运行，Agent 不能崩了就没。

## 1. 三类 Agent 记忆

| 记忆类型 | 存储内容 | 生存期 | 比赛中的用途 |
|----------|---------|--------|-------------|
| **短期/会话** | 当前对话历史 | 一次会话 | Agent 与用户的连续问答 |
| **长期/跨会话** | 用户偏好、历史记录 | 持久化 | 多轮数据分析和查询 |
| **工具调用** | API 调用结果缓存 | 按需 | 避免重复查询相同数据 |

## 2. LangGraph 记忆持久化（如果使用 LangGraph）

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

# 内存检查点 — 自动保存每一步状态
memory = MemorySaver()

graph = StateGraph(AgentState)
# ... 定义节点和边 ...
app = graph.compile(checkpointer=memory)

# 每次调用自动保存/恢复状态
config = {"configurable": {"thread_id": "session-1"}}
result = app.invoke({"messages": [user_message]}, config)
# 下次调用同一 thread_id 自动恢复上下文
```

## 3. AgentCore Memory（如果使用 AgentCore）

```python
from bedrock_agentcore import AgentMemory

# AgentCore 内置记忆
memory = AgentMemory(
    memory_type="episodic",   # 情景记忆：记录 Agent 做了什么
    retention_policy={
        "max_episodes": 1000,
        "decay_factor": 0.95
    }
)

# Agent 自动记录每次交互
memory.record_episode(
    context=session_context,
    action_taken=agent_action,
    outcome=result,
    feedback=user_feedback
)
```

## 4. 错误恢复模式

### 模式 A：重试 + 指数退避
```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1.0):
    """Agent 工具调用的重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
            return {"error": str(last_error), "status": "failed"}
        return wrapper
    return decorator

@retry_with_backoff(max_retries=2)
def query_draft_data(query):
    # 查询选秀数据
    pass
```

### 模式 B：Agent 级降级
```python
# 主方案 → 备选方案 → 兜底
async def predict_with_fallback(team, pick, players):
    try:
        # Tier 1: 完整模型预测
        return await full_model_predict(team, pick, players)
    except ModelError:
        # Tier 2: 简化规则预测
        return await rule_based_predict(team, pick, players)
    except Exception:
        # Tier 3: 基于历史平均
        return await historical_avg_predict(team, pick)
```

### 模式 C：断点续传
```python
# 长时任务分步保存，崩溃后恢复
import json

class TaskRecovery:
    def __init__(self, task_id):
        self.task_id = task_id
        self.state_file = f"/tmp/task_{task_id}.json"
    
    def save_progress(self, step, data):
        with open(self.state_file, "w") as f:
            json.dump({"step": step, "data": data}, f)
    
    def load_progress(self):
        try:
            with open(self.state_file) as f:
                return json.load(f)
        except FileNotFoundError:
            return {"step": 0, "data": None}
    
    def run_pipeline(self):
        state = self.load_progress()
        if state["step"] < 1:
            data = self.step1()
            self.save_progress(1, data)
        if state["step"] < 2:
            data = self.step2(state["data"])
            self.save_progress(2, data)
        # ...
```

## 5. 比赛日检查清单

| 场景 | 做法 |
|------|------|
| Agent 调用工具超时 | 重试 2 次 + 降级到简单规则 |
| API 限流 | 指数退避 + 队列 |
| 模型响应格式不对 | 结构化输出的 schema 校验 + 重新提词 |
| 数据加载失败 | 本地缓存副本 |
| 会话断开 | 用 AgentCore Session 管理，session_id 恢复 |
| 长时任务中断 | 分步存档，支持续传 |
