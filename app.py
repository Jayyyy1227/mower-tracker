import streamlit as st
import requests

# 把刚刚从 Google 复制的网址粘贴到这里
GOOGLE_API_URL = "https://script.google.com/macros/s/AKfycbxpViohC47nzS_AlfZKqCHVv9PvaY7b0q_L2bPpe1lzGQehkj7Rd5EdiQsm5EeZR9zlWg/exec"

st.title("🚜 割草机器人售后追踪系统")

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
        # 打包成 JSON 发送
        payload = {
            "country": country,
            "reporter": reporter,
            "sn": sn,
            "model": model,
            "desc": desc
        }
        # 发送请求给 Google
        response = requests.post(GOOGLE_API_URL, json=payload)
        
        if response.text == "Success":
            st.success("🎉 数据已实时同步到你的 Google Sheets！")
        else:
            st.error("提交失败，请检查网址。")