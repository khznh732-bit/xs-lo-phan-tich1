import streamlit as st
import pandas as pd
import requests
from collections import Counter
from datetime import datetime
import numpy as np

st.set_page_config(page_title="AI Xổ Số PRO", layout="wide")
st.title("🤖 AI Phân Tích Giải Đặc Biệt PRO")

# ===== LẤY DỮ LIỆU =====
@st.cache_data(ttl=600)
def fetch_data(region, days):
    url = "https://xoso.dev/api/mb.json" if region=="Miền Bắc" else "https://xoso.dev/api/mn.json"
    r = requests.get(url, timeout=10)
    data = r.json()["data"][:days]
    df = pd.DataFrame(data)
    df["special"] = df["giai_dac_biet"].astype(str)
    df["two"] = df["special"].str[-2:]
    df["date"] = pd.to_datetime(df["date"])
    return df

# ===== AI =====
def ai_analysis(df):
    two_digits = df["two"].tolist()
    counter_total = Counter(two_digits)
    counter_recent = Counter(two_digits[:7])

    df["weekday"] = df["date"].dt.weekday
    today_w = datetime.now().weekday()
    counter_weekday = Counter(df[df["weekday"]==today_w]["two"])

    all_numbers = [f"{i:02d}" for i in range(100)]
    results = []

    for num in all_numbers:
        freq = counter_total.get(num, 0)
        recent_freq = counter_recent.get(num, 0)
        week_freq = counter_weekday.get(num, 0)

        # GAN
        gan = 0
        for d in two_digits:
            if d != num:
                gan += 1
            else:
                break

        # ===== PHÁT HIỆN BẤT THƯỜNG (SẮP NỔ) =====
        expected = np.mean(list(counter_total.values()))
        anomaly = (gan > expected*2) or (recent_freq==0 and freq>expected)

        score = (freq*2.5)+(recent_freq*3)+(gan*1.2)+(week_freq*2)
        if anomaly:
            score *= 1.5  # tăng trọng số nếu có dấu hiệu

        results.append({
            "Số": num,
            "Tần suất": freq,
            "7 ngày": recent_freq,
            "Cùng thứ": week_freq,
            "Gan": gan,
            "🔥 Sắp nổ": "⚠️" if anomaly else "",
            "Điểm AI": round(score,2)
        })

    df_res = pd.DataFrame(results)
    return df_res.sort_values(by="Điểm AI", ascending=False)

# ===== UI =====
col1, col2 = st.columns(2)
region = col1.selectbox("Chọn miền", ["Miền Bắc","Miền Nam"])
days = col2.slider("Số ngày phân tích", 30, 120, 60)

if st.button("🚀 Chạy AI"):
    try:
        df_data = fetch_data(region, days)
        result = ai_analysis(df_data)

        st.subheader(f"🎯 TOP 12 AI – {region}")
        st.dataframe(result.head(12))
        st.bar_chart(result.head(10).set_index("Số"))

        st.subheader("🔥 SỐ CÓ DẤU HIỆU SẮP NỔ")
        hot = result[result["🔥 Sắp nổ"]=="⚠️"].head(6)
        if not hot.empty:
            st.dataframe(hot)
        else:
            st.write("Chưa phát hiện bất thường mạnh.")

    except:
        st.error("Không lấy được dữ liệu.")
