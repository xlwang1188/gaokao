import streamlit as st
import pandas as pd
from urllib.parse import quote

st.set_page_config(layout="wide", page_title="综合评价录取分析")

hide_st_style = """
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


# --- 数据加载函数 ---
@st.cache_data
def load_comprehensive_assessment_data():
    try:
        df = pd.read_csv('admissions_zp_2024.csv', encoding='utf-8-sig')
        return df

    except FileNotFoundError:
        st.error("错误：未找到 `admissions_zp_2024.csv` 文件。")
        return None


# --- 主应用 ---
df_comp = load_comprehensive_assessment_data()

if df_comp is None or df_comp.empty:
    st.warning("综合评价数据加载失败或数据为空。")
    st.stop()

# --- 侧边栏查询 ---
st.sidebar.header("🔍 查询条件")
university_list_comp = sorted(df_comp['院校名称'].unique())

# 检查URL参数以支持从首页跳转
query_params = st.query_params
default_index = 0
if 'university' in query_params:
    try:
        default_university = query_params.get("university")
        default_index = university_list_comp.index(default_university)
    except ValueError:
        default_index = 0  # 如果URL中的大学不在列表中，则使用默认值

selected_university_comp = st.sidebar.selectbox(
    "选择院校",
    options=university_list_comp,
    index=default_index,
    key="comp_uni_select"
)

# --- 按院校查询 ---
st.header(f"{selected_university_comp} 2024年综合评价录取详情")
uni_details_df = df_comp[df_comp['院校名称'] == selected_university_comp]

if not uni_details_df.empty:
    detail_cols = ['专业组名称', '专业名称', '录取人数', '最高分', '最低分', '平均分', '最低分排位', '平均分排位']

    # 动态计算表格高度，避免出现内部滚动条
    # (表头高度约35px) + (每行高度约36px * 行数) + (一点额外边距)
    table_height = 35 + len(uni_details_df) * 36 + 2

    st.dataframe(
        uni_details_df[detail_cols].sort_values(by='平均分排位'),
        hide_index=True,
        use_container_width=True,
        height=table_height,  # 设置表格高度
        column_config={"专业名称": st.column_config.TextColumn(width="large"),
                       "专业组名称": st.column_config.TextColumn(width="medium")}
    )
else:
    st.error("未找到该院校的综合评价数据。")