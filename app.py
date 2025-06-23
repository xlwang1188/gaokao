import streamlit as st

# 页面配置，设置浏览器标签页的标题和图标
st.set_page_config(
    page_title="上海高考数据分析平台",
    page_icon="🎓",
    layout="wide"
)

# --- 页面主内容 ---

# 1. 标题和欢迎语
st.title("🎓 上海高考数据分析平台")
st.markdown("---")
st.markdown("欢迎使用本平台！请通过左侧的导航栏选择您需要的功能。")

# 2. 功能模块介绍 (使用卡片式布局)
st.header("主要功能模块")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("🥇 普通本科批次分析")
        st.markdown("""
        - **投档排名查询**: 根据您的预估排位，查找近三年普通批次中分数线相近的院校专业组。
        - **投档趋势分析**: 查看指定院校在近三年普通批次的投档分数和排位变化趋势。
        """)
        st.page_link("pages/3_普通本科投档排名查询.py", label="进入普通批次排名查询", icon="🔍")
        st.page_link("pages/4_普通本科投档趋势分析.py", label="进入普通批次趋势分析", icon="📈")


with col2:
    with st.container(border=True):
        st.subheader("🧭 综合评价批次分析 (2024年)")
        st.markdown("""
        - **综评排名查询**: 根据您的预估排位，查找2024年综合评价批次中录取平均分相近的专业。
        - **综评录取详情**: 查看指定院校在2024年综合评价批次中，各专业的详细录取情况。
        """)
        st.page_link("pages/1_综评排名查询.py", label="进入综评排名查询", icon="🧭")
        st.page_link("pages/2_综合评价分析.py", label="进入综评院校分析", icon="📊")

st.markdown("---")
st.info("数据来源：您提供的CSV文件。所有数据和分析仅供参考，请以官方发布为准。")