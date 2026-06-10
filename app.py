"""DraftCode 选秀预测 Agent — Web UI

比赛交付物#1：可访问、可交互的 Web Agent 界面。
Streamlit 应用，连接 Bedrock Agent 提供选秀预测分析。

Usage:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 页面配置
st.set_page_config(
    page_title="NBA Draft Predictor",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================
# 模拟数据（TODO 6/16: 替换为真实数据+模型）
# ============================================
@st.cache_data
def load_mock_predictions() -> pd.DataFrame:
    """模拟30队预测结果"""
    teams = [
        "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets",
        "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets",
        "Detroit Pistons", "Golden State Warriors", "Houston Rockets", "Indiana Pacers",
        "LA Clippers", "Los Angeles Lakers", "Memphis Grizzlies", "Miami Heat",
        "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans",
        "New York Knicks", "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers",
        "Phoenix Suns", "Portland Trail Blazers", "Sacramento Kings",
        "San Antonio Spurs", "Toronto Raptors", "Utah Jazz", "Washington Wizards",
    ]
    np.random.seed(42)
    data = []
    for i, team in enumerate(teams, 1):
        pick = i
        confidence = round(np.random.uniform(0.55, 0.95), 2)
        top_player = f"Player_{pick}"
        data.append({
            "Pick": pick,
            "Team": team,
            "Predicted Player": top_player,
            "Confidence": confidence,
            "Confidence Label": f"{confidence*100:.0f}%",
        })
    return pd.DataFrame(data)


def get_agent_response(query: str) -> str:
    """TODO: 接入 agent_app.py 的 DraftAgent"""
    # 临时返回模拟响应
    return f"📊 分析结果：基于历史数据模式，该顺位预计选择 **Player_X**（置信度 78%）。\n\n> 关键因子：位置需求匹配 + 体测数据优势 + 大学效率指标领先。"


# ============================================
# 侧边栏
# ============================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/nba.png", width=64)
    st.title("🏀 NBA Draft")
    st.markdown("---")
    st.markdown("**AWS × CSDN DraftCode**")
    st.markdown("24h 黑客松 · 选秀预测 Agent")
    st.markdown("---")

    st.subheader("📋 快速查询")
    quick_queries = [
        "预测马刺队#4顺位的选择",
        "分析前5顺位最可能的球员",
        "前十顺位中有几个后卫？",
        "哪支球队最可能向上交易？",
    ]
    for q in quick_queries:
        if st.button(q, use_container_width=True, type="secondary"):
            st.session_state.query = q

    st.markdown("---")
    st.caption("数据来源：26年NBA选秀历史数据")
    st.caption("模型：XGBoost + Claude Sonnet")


# ============================================
# 主界面
# ============================================
st.title("🏀 NBA 选秀预测 Agent")
st.markdown("基于 26 年历史数据 + 机器学习，预测 30 支球队首轮选秀结果")

# Tab 布局
tab1, tab2, tab3 = st.tabs(["📊 预测面板", "💬 对话查询", "📋 全部结果"])

# ===== Tab 1: 预测面板 =====
with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🏆 预测选秀结果")

        # 顶部顺位高亮
        top5 = ["#1", "#2", "#3", "#4", "#5"]
        top_cols = st.columns(5)
        mock = load_mock_predictions()
        for i, (col, pick_num) in enumerate(zip(top_cols, top5)):
            row = mock.iloc[i]
            with col:
                st.metric(
                    label=f"Pick {pick_num}",
                    value=row["Team"].split()[-1],
                    delta=row["Confidence Label"],
                )
                st.caption(row["Predicted Player"])

        # 完整表格
        st.markdown("---")
        st.dataframe(
            mock,
            column_config={
                "Pick": st.column_config.NumberColumn("顺位"),
                "Team": "球队",
                "Predicted Player": "预测球员",
                "Confidence": st.column_config.ProgressColumn(
                    "置信度", format="%.0f", min_value=0, max_value=1
                ),
            },
            hide_index=True,
            use_container_width=True,
        )

    with col2:
        st.subheader("📈 关键指标")
        st.metric("平均置信度", "78%", delta="+5% vs 基线")
        st.metric("Top-5 命中率", "80%", delta="待验证")
        st.metric("Top-10 准确率", "70%", delta="待验证")

        st.markdown("---")
        st.subheader("🏀 最看好球员 Top 3")
        st.success("1. Player_1 — 综合评分 92")
        st.info("2. Player_5 — 综合评分 88")
        st.warning("3. Player_3 — 综合评分 85")

# ===== Tab 2: 对话查询 =====
with tab2:
    st.subheader("💬 向 Agent 提问")

    # 初始化聊天历史
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "query" not in st.session_state:
        st.session_state.query = ""

    # 预填查询
    if st.session_state.query:
        initial_query = st.session_state.query
        st.session_state.query = ""
        st.session_state.messages.append({"role": "user", "content": initial_query})
        with st.chat_message("user"):
            st.markdown(initial_query)
        with st.chat_message("assistant"):
            with st.spinner("Agent 正在分析..."):
                response = get_agent_response(initial_query)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # 显示历史
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 输入框
    if prompt := st.chat_input("输入你的选秀问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Agent 正在分析..."):
                response = get_agent_response(prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# ===== Tab 3: 全部结果 =====
with tab3:
    st.subheader("📋 30 支球队完整预测结果")

    mock = load_mock_predictions()

    # 可视化
    fig = px.bar(
        mock,
        x="Team",
        y="Confidence",
        color="Confidence",
        color_continuous_scale="Viridis",
        title="各顺位预测置信度",
        labels={"Team": "球队", "Confidence": "置信度"},
    )
    fig.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # 可搜索表格
    search = st.text_input("🔍 搜索球队或球员", "")
    filtered = mock[
        mock["Team"].str.contains(search, case=False)
        | mock["Predicted Player"].str.contains(search, case=False)
    ]
    st.dataframe(filtered, hide_index=True, use_container_width=True)

    # 导出
    csv = mock.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 下载预测结果 CSV",
        data=csv,
        file_name="draft_predictions.csv",
        mime="text/csv",
    )

# 页脚
st.markdown("---")
st.caption("DraftCode 24h Hackathon · AWS × CSDN · 2026")
