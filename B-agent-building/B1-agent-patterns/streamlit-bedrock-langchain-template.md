# Streamlit + LangChain + Bedrock 快速模板

> FAST 的轻量替代方案。如果 React 太重，用 Streamlit 几行 Python 搭 Web Agent 界面。
> 比赛评分 30% 代码质量 + 30% 路演 — 简单好用的 UI 比复杂的框架更重要。

## 来源

- **GitHub (官方示例)**: https://github.com/aws-samples/streamlit-examples-for-bedrock
- **LangChain Streamlit 集成**: https://www.langchain.com/blog/langchain-streamlit
- **Bedrock AgentCore + Streamlit 部署指南**: https://newmathdata.com/blog/aws-bedrock-agentcore-runtime-streamlit-frontend-deployment

## 核心模板（3 个文件）

### app.py
```python
import streamlit as st
import boto3
from langchain_aws import ChatBedrock

st.set_page_config(page_title="Draft Predictor", layout="wide")
st.title("🏀 NBA Draft 选秀预测 Agent")

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
llm = ChatBedrock(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    client=bedrock_runtime,
    temperature=0.3,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("输入你的选秀问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        response = llm.invoke(prompt)
        st.markdown(response.content)
        st.session_state.messages.append({"role": "assistant", "content": response.content})
```

### requirements.txt
```
streamlit>=1.35
boto3>=1.34
langchain-aws>=0.2
pandas
numpy
plotly
```

## 官方示例一览

| 文件 | 功能 | 难度 |
|------|------|------|
| `1-chat.py` | 基础 Bedrock Chat | ⭐ |
| `2-langchain_app.py` | LangChain 简单应用 | ⭐⭐ |
| `3-langchain_agent.py` | LangChain Agent（带工具） | ⭐⭐⭐ |
| `4-langchain_chat.py` | LangChain 聊天历史 | ⭐⭐ |
| `5-llamaindex_rag_chat.py` | LlamaIndex RAG | ⭐⭐⭐ |
| `6-bedrock-claude3-streaming-demo.py` | 流式响应 | ⭐⭐ |
