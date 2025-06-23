import streamlit as st
import pandas as pd
from urllib.parse import quote

# Streamlit页面配置
st.set_page_config(layout="wide", page_title="上海高考排位查询")

hide_st_style = """
            <style>
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* 减小主内容区的顶部内边距 */
            .main .block-container {
                padding-top: 1rem;
                padding-bottom: 1rem;
            }
            
            /* 隐藏侧边栏的折叠箭头 */
            button[title="View fullscreen"] {
                visibility: hidden;
            }
            button[title="Collapse sidebar"] {
                visibility: hidden;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


@st.cache_data
def load_data():
    """从预处理好的CSV加载数据"""
    try:
        df = pd.read_csv('gaokao22_24.csv')
        return df
    except FileNotFoundError:
        st.error("错误：未找到 `gaokao22_24.csv` 文件。请先运行 `preprocess_data.py` 脚本。")
        st.stop()


# --- 主应用 ---
df = load_data()

# --- Sidebar for user inputs ---
st.sidebar.header("🔍 查询条件")
year = st.sidebar.selectbox("选择年份", options=sorted(df['年份'].unique(), reverse=True), key='year_select')
target_rank = st.sidebar.number_input("输入你的目标排位", min_value=1, value=5000, step=100)
tolerance = st.sidebar.slider("设置排位浮动范围 (±)", min_value=100, max_value=5000, value=500, step=100)
st.sidebar.info("在下方表格中点击院校名称，可跳转至该校的详细投档趋势分析页面。")

# --- Main panel for displaying results ---
st.header(f"📊 {year}年 排位 {target_rank - tolerance} - {target_rank + tolerance} 的院校专业组")

year_df = df[df['年份'] == year].copy()
year_df['排位差'] = (year_df['投档排位'] - target_rank).abs()
result_df = year_df[year_df['排位差'] <= tolerance].sort_values('投档排位').reset_index(drop=True)

if result_df.empty:
    st.warning("在指定范围内未找到任何匹配的专业组。")
else:
    # 创建可点击的链接
    result_df['院校名称'] = result_df['院校名称'].apply(
        lambda x: f"[{x}](普通本科投档趋势分析?university={quote(x)})"
    )

    # 为了更好的展示，隐藏了专业列表
    display_df = result_df[['院校名称', '专业组代码', '专业组名称', '投档分数', '投档排位']]

    st.markdown(display_df.to_markdown(index=False), unsafe_allow_html=True)

    # 提供一个可展开的区域来查看完整的专业列表
    with st.expander("点击查看上述结果包含的专业列表 (仅2024年数据)"):
        st.dataframe(result_df[['院校名称', '专业组名称', '专业列表']], use_container_width=True)