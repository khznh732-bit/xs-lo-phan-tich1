import streamlit as st
import pandas as pd
from collections import Counter
from datetime import datetime
import numpy as np

st.set_page_config(page_title="AI Lô 2 Số", layout="wide")
st.title("🤖 AI Phân Tích Lô 2 Số (Nhập Tay)")

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["date", "special"])

# ===== NHẬP DỮ LIỆU =====
st.subheader("📥 Nhập giải đặc biệt")

col1, col2 = st.columns(2)
date = col1.date_input("Ngày")
special = col2.text_input("Giải đặc biệt (5 số)")

if st.button("➕ Thêm dữ liệu"):
    if len(special) == 5 and special.isdigit():
        new_row = pd.DataFrame([[date, special]], columns=["date","special"])
        st.session_state.data = pd.concat([new_row, st.session_state.data], ignore_index=True)
        st.success("Đã thêm!")
    else:
        st.error("Nhập đủ 5 số.")

st.subheader("📋 Dữ liệu đã nhập")
st.dataframe(st.session_state.data)

# ===== AI PHÂN TÍCH =====
def ai_analysis(df):
    df["two"] = df["special"].str[-2:]
    two_digits = df["two"].tolist()

    counter_total = Counter(two_digits)
    counter_recent = Counter(two_digits[:7])

    df["weekday"] = pd.to_datetime(df["date"]).dt.weekday
    today_w = datetime.now().weekday()
    counter_weekday = Counter(df[df["weekday"]==today_w]["two"])

    avg_freq = np.mean(list(counter_total.values()))

    all_numbers = [f"{i:02d}" for i in range(100)]
    results = []

    for num in all_numbers:
        freq = counter_total.get(num, 0)
        recent = counter_recent.get(num, 0)
        week = counter_weekday.get(num, 0)

        gan = 0
        for d in two_digits:
            if d != num:
                gan += 1
            else:
                break

        anomaly = (gan > avg_freq*2) or (recent==0 and freq>avg_freq)

        score = (freq*2.5)+(recent*3)+(gan*1.2)+(week*2)
        if anomaly:
            score *= 1.5

        results.append({
            "Số": num,
            "Tần suất": freq,
            "7 ngày": recent,
            "Cùng thứ": week,
            "Gan": gan,
            "🔥 Sắp nổ": "⚠️" if anomaly else "",
            "Điểm AI": round(score,2)
        })

    df_res = pd.DataFrame(results)
    return df_res.sort_values(by="Điểm AI", ascending=False)

# ===== CHẠY AI =====
if st.button("🚀 Chạy AI"):
    if len(st.session_state.data) < 10:
        st.warning("Nhập ít nhất 10 ngày dữ liệu.")
    else:
        result = ai_analysis(st.session_state.data.copy())

        st.subheader("🎯 TOP 12 AI")
        st.dataframe(result.head(12))
        st.bar_chart(result.head(10).set_index("Số"))

        st.subheader("🔥 SỐ CÓ DẤU HIỆU SẮP NỔ")
        hot = result[result["🔥 Sắp nổ"]=="⚠️"].head(6)
        if not hot.empty:
            st.dataframe(hot)
        else:
            st.write("Chưa có số bất thường mạnh.")
