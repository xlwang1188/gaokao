import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="普通本科投档趋势分析")

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

# CSS样式保持不变
TABLE_STYLE = """
<style>
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }
    .custom-table th, .custom-table td {
        border: 1px solid #e1e4e8;
        padding: 8px;
        text-align: left;
        word-wrap: break-word;
        word-break: break-all;
    }
    .custom-table th {
        background-color: #f6f8fa;
        font-weight: bold;
    }
    .custom-table tr:nth-child(even) {
        background-color: #fcfcfc;
    }
    .col-group-name { width: 20%; }
    .col-group-code { width: 10%; }
    .col-major-list { width: 70%; }
</style>
"""
st.markdown(TABLE_STYLE, unsafe_allow_html=True)


@st.cache_data
def load_main_data():
    """加载主趋势数据"""
    try:
        df = pd.read_csv('gaokao22_24.csv')
        return df
    except FileNotFoundError:
        st.error("错误：未找到 `gaokao22_24.csv` 文件。")
        st.stop()


@st.cache_data
def load_admission_details():
    """加载2024年详细录取数据"""
    try:
        dtype_map = {
            'major_group_code': str, 'enrollment_count': 'Int64', 'highest_score': 'Int64',
            'lowest_score': 'Int64', 'average_score': 'Int64', 'lowest_rank': 'Int64',
            'average_rank': 'Int64'
        }
        df = pd.read_csv('admissions_2024.csv', encoding='utf-8-sig', dtype=dtype_map)
        df.rename(columns={
            'major_name': '专业名称', 'enrollment_count': '招生人数', 'highest_score': '最高分',
            'lowest_score': '最低分', 'average_score': '平均分', 'lowest_rank': '最低分排位',
            'average_rank': '平均分排位'
        }, inplace=True)
        return df
    except FileNotFoundError:
        st.warning("警告：未找到 `admissions_2024.csv` 文件。将无法显示详细专业录取数据。")
        return None


def generate_html_table(df):
    """生成专业组列表的HTML表格"""
    html_string = '<table class="custom-table"><thead><tr><th class="col-group-name">专业组名称</th><th class="col-group-code">专业组代码</th><th class="col-major-list">包含专业 (2024年)</th></tr></thead><tbody>'
    for _, row in df.iterrows():
        html_string += f"<tr><td>{row['专业组名称']}</td><td>{row['专业组代码']}</td><td>{row['专业列表']}</td></tr>"
    html_string += "</tbody></table>"
    return html_string


# --- 主应用逻辑 ---
df_main = load_main_data()
df_details_2024 = load_admission_details()
university_list = sorted(df_main['院校名称'].dropna().unique())

# --- 侧边栏查询控件 ---
st.sidebar.header("🔍 查询条件")

# --- 用户输入与模糊查询 ---
query_params = st.query_params
if 'university' in query_params and 'university_search_term' not in st.session_state:
    default_university = query_params.get('university')
    if default_university in university_list:
        st.session_state.university_search_term = default_university
    st.query_params.clear()

if 'university_search_term' not in st.session_state:
    st.session_state.university_search_term = "上海大学"

search_term = st.sidebar.text_input(
    "输入院校名称进行模糊查询",
    value=st.session_state.university_search_term,
    help="输入部分或完整院校名称后按回车键进行搜索"
)
st.session_state.university_search_term = search_term

if search_term:
    matches = [uni for uni in university_list if search_term.lower() in uni.lower()]
else:
    matches = university_list

if not matches:
    st.error(f"未找到与 '{search_term}' 相关的院校。")
    st.stop()
elif len(matches) > 1:
    selected_university = st.sidebar.selectbox(f"找到 {len(matches)} 个匹配项，请选择一个查看：", options=matches)
else:
    selected_university = matches[0]



uni_df = df_main[df_main['院校名称'] == selected_university]

if not uni_df.empty:
    st.subheader(f"📚 {selected_university} 在2024年的专业组列表")
    summary_2024 = uni_df[uni_df['年份'] == 2024][['专业组代码', '专业组名称', '专业列表']].drop_duplicates()
    if not summary_2024.empty:
        html_table = generate_html_table(summary_2024)
        st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.info("未找到该校2024年的专业组概览数据。")

    st.subheader(f"📊 {selected_university} 投档趋势图表")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 投档分数线变化趋势")
        fig_score = px.line(uni_df, x='年份', y='投档分数', color='专业组名称', markers=True,
                            hover_data={'年份': True, '投档分数': True, '投档排位': True, '专业组代码': True})
        fig_score.update_layout(legend_title_text='专业组', xaxis_title=None, yaxis_title="投档分数",
                                xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig_score, use_container_width=True)

    with col2:
        st.markdown("##### 投档排位变化趋势")
        fig_rank = px.line(uni_df, x='年份', y='投档排位', color='专业组名称', markers=True,
                           hover_data={'年份': True, '投档分数': True, '投档排位': True, '专业组代码': True})
        fig_rank.update_layout(legend_title_text='专业组', xaxis_title=None, yaxis_title="投档排位 (越低越靠前)",
                               xaxis=dict(tickmode='linear', dtick=1), yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_rank, use_container_width=True)

    if df_details_2024 is not None:
        st.markdown("---")
        st.subheader("🔍 2024年各专业录取详情 (普通本科批次)")

        uni_details_2024 = df_details_2024[df_details_2024['university_name'] == selected_university]

        # *** 关键修改：只保留 'batch' 列为 '普通本科' 的数据 ***
        uni_details_2024_filtered = uni_details_2024[uni_details_2024['batch'] == '普通本科']

        if uni_details_2024_filtered.empty:
            st.info("该院校在2024年普通本科批次下暂无详细专业录取数据。")
        else:
            group_options = sorted(uni_details_2024_filtered['major_group_name'].unique())
            if group_options:
                selected_group_for_details = st.selectbox("请选择要查看的专业组：", options=group_options)

                group_details = uni_details_2024_filtered[
                    uni_details_2024_filtered['major_group_name'] == selected_group_for_details]

                display_cols = ['专业名称', '招生人数', '最高分', '最低分', '平均分', '最低分排位', '平均分排位']

                table_height = 35 + len(uni_details_2024_filtered) * 36 + 2

                st.dataframe(
                    group_details[display_cols].reset_index(drop=True),
                    use_container_width=True,
                    hide_index=True,
                    height=table_height,  # 设置表格高度
                )
else:
    st.info("请选择一所院校以查看其数据。")