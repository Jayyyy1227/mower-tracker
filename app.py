import streamlit as st
import pandas as pd
import requests

# 1. 你提交数据用的 Apps Script 网址
GOOGLE_API_URL = "https://script.google.com/macros/s/AKfycbxpViohC47nzS_AlfZKqCHVv9PvaY7b0q_L2bPpe1lzGQehkj7Rd5EdiQsm5EeZR9zlWg/exec"

# 2. 你刚才获取的读取数据用的 CSV 网址
GOOGLE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTVvG9Q2rMJOnDbR1P6PrbC5hGOlz5x3EO1GfFJfsawOS10Q7N85FH2AiB60B8HbPa9yoz5beOdhQ39/pub?gid=1174112572&single=true&output=csv"

st.set_page_config(page_title="割草机追踪系统", layout="wide")
st.title("🚜 割草机器人售后追踪系统")

tab1, tab2 = st.tabs(["📝 提交新工单", "📊 数据显示面板"])

# ==========================================
# Tab 1: 提交面板 (保持不变)
# ==========================================
with tab1:
    with st.form("submit_form"):
        col1, col2 = st.columns(2)
        with col1:
            country = st.text_input("国家")
            reporter = st.text_input("报告人")
        with col2:
            sn = st.text_input("机器 SN 码")
            model = st.selectbox("型号", ["R5 Mini", "R5 Regular"])
        desc = st.text_area("问题描述")
        
        if st.form_submit_button("提交到总表"):
            payload = {"country": country, "reporter": reporter, "sn": sn, "model": model, "desc": desc}
            response = requests.post(GOOGLE_API_URL, json=payload)
            if response.text == "Success":
                st.success("🎉 数据已实时同步到你的 Google Sheets！")
            else:
                st.error("提交失败，请检查 API 网址。")

# ==========================================
# Tab 2: 显示面板 (你要修改的地方在这里)
# ==========================================
with tab2:
    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.subheader("📊 实时工单数据看板")
    with col_btn:
        # 加一个手动刷新按钮，方便查看最新数据
        if st.button("🔄 刷新数据"):
            st.rerun()

    try:
        # 直接通过 pandas 读取 CSV 链接，完全不需要复杂的鉴权！
        df = pd.read_csv(GOOGLE_CSV_URL)
        
        # --- 下面是你可以自定义修改的面板功能 ---
        
        # 💡 修改 1：添加一个 SN 码搜索框
        search_sn = st.text_input("🔍 输入机器 SN 码进行快速搜索:")
        if search_sn:
            # 过滤出包含该 SN 的行 (假设你的列名叫 '机器 SN 码'，请根据实际表头修改)
            # 因为数据可能是数字或文本，统一转为字符串进行比对
            df = df[df.astype(str).apply(lambda x: x.str.contains(search_sn, case=False, na=False)).any(axis=1)]
            
        # 💡 修改 2：如果你只想在网页上显示特定的几列，可以取消下面这行的注释
        # df = df[['报告人', '机器 SN 码', '问题描述']] 
        
        # 💡 修改 3：让最新提交的数据排在最上面 (假设表格默认是往下追加的)
        df = df.iloc[::-1].reset_index(drop=True)

        # 最终展示表格
        st.dataframe(df, use_container_width=True, height=500)

    except Exception as e:
        st.warning("暂无数据或无法加载。请确保已将 Google 表格发布为 Web CSV。")
