import streamlit as st
import requests
import pandas as pd
import datetime

# ==========================================
# 1. 核心配置 (请替换为你自己的网址！)
# ==========================================
# 这里填你从 Google Apps Script 拿到的 /exec 结尾的网址 (用于提交数据)
GOOGLE_API_URL = "https://script.google.com/macros/s/你的那一长串代码/exec"

# 这里填你从 Google 表格“发布到网络”拿到的 /pub?output=csv 结尾的网址 (用于读取数据)
GOOGLE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-你的那一长串/pub?output=csv"

# ==========================================
# 2. 页面全局设置
# ==========================================
st.set_page_config(page_title="售后工单追踪系统", layout="wide")
st.title("🚜 割草机器人全球售后追踪系统")

# 创建两个标签页
tab1, tab2 = st.tabs(["📝 提交新工单 (填写入口)", "📊 实时数据看板"])

# ==========================================
# Tab 1: 完整数据录入表单
# ==========================================
with tab1:
    st.info("💡 请在下方填写工单的所有信息，点击提交后将自动写入云端总表。")
    
    with st.form("full_submit_form", clear_on_submit=True):
        # 使用 3 列排版，让界面更紧凑专业
        col1, col2, col3 = st.columns(3)
        
        with col1:
            report_date = st.date_input("报告日期", datetime.date.today())
            reporter = st.text_input("报告人姓名/邮箱 *")
            country = st.selectbox("国家/地区", ["USA", "Canada", "Germany", "Sweden", "Italy", "China", "Other"])
            
        with col2:
            model = st.selectbox("机器型号", ["R5 Mini", "R5 Regular", "R5 Pro", "Other"])
            sn = st.text_input("机器 SN 码 *")
            firmware = st.text_input("当前固件版本 (如 1.4.21)")
            
        with col3:
            fault_code = st.text_input("故障代码 (Event ID)")
            severity = st.selectbox("严重程度", ["A (轻微)", "W (警告)", "E (错误)", "F (致命)"])
            status = st.selectbox("当前状态", ["Pending (待处理)", "In Progress (处理中)", "Closed (已关闭)"])

        # 横跨整行的长文本输入框
        desc = st.text_area("问题详细描述 (Description) *", height=100)
        
        st.markdown("---")
        # 提交按钮
        submitted = st.form_submit_button("🚀 一键提交至总表", use_container_width=True)
        
        if submitted:
            if not reporter or not sn or not desc:
                st.warning("⚠️ 请填写带 * 的必填项 (报告人、SN码、问题描述)！")
            else:
                # 打包所有数据
                payload = {
                    "date": report_date.strftime("%Y-%m-%d"),
                    "reporter": reporter,
                    "country": country,
                    "model": model,
                    "sn": sn,
                    "firmware": firmware,
                    "fault_code": fault_code,
                    "severity": severity,
                    "status": status,
                    "desc": desc
                }
                
                # 发送给 Google
                with st.spinner('正在安全同步数据到云端...'):
                    try:
                        response = requests.post(GOOGLE_API_URL, json=payload)
                        if response.text == "Success":
                            st.success(f"🎉 提交成功！SN: {sn} 的工单已录入系统。")
                        else:
                            st.error(f"⚠️ 提交失败！谷歌返回信息: {response.text}")
                    except Exception as e:
                        st.error(f"网络请求失败，请检查 API 网址。错误详情: {e}")


# ==========================================
# Tab 2: 数据显示与查询面板
# ==========================================
with tab2:
    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.subheader("📊 云端工单总表")
    with col_btn:
        # 手动刷新按钮
        if st.button("🔄 刷新最新数据", use_container_width=True):
            st.rerun()

    try:
        # 直接读取 CSV 链接展示数据
        df = pd.read_csv(GOOGLE_CSV_URL)
        
        # 将空值填充为空白，避免显示 NaN
        df = df.fillna("")
        
        # 增加搜索功能：输入 SN 码或报告人搜索
        search_kw = st.text_input("🔍 快速搜索 (输入 SN 码、报告人或国家):")
        if search_kw:
            # 在所有列中模糊匹配搜索词
            mask = df.astype(str).apply(lambda x: x.str.contains(search_kw, case=False)).any(axis=1)
            df = df[mask]
            
        # 让最新提交的数据排在最上面 (倒序排列)
        df = df.iloc[::-1].reset_index(drop=True)

        # 在网页上展示漂亮的表格
        st.dataframe(df, use_container_width=True, height=600)

    except Exception as e:
        st.warning("⚠️ 暂无数据或无法加载。请确保已在谷歌表格中点击了“发布到网络”并选择了 CSV 格式。")
