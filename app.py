import streamlit as st
import pandas as pd
import requests
from collections import Counter

st.set_page_config(page_title="AI Dự Đoán Lô", layout="wide")
st.title("🤖 AI Phân Tích Giải Đặc Biệt (Tự Động)")

# ===== LẤY DỮ LIỆU ONLINE =====
@st.cache_data(ttl=600)
def fetch_data(days):
    url = "https://xoso.dev/api/mb.json"
    r = requests.get(url, timeout=10)
    data = r.json()["data"][:days]
    specials = [str(x["giai_dac_biet"]) for x in data]
    return [s[-2:] for s in specials]

# ===== AI TÍNH TOÁN =====
def ai_analysis(two_digits):
    counter_total = Counter(two_digits)
    recent = two_digits[-7:]
    counter_recent = Counter(recent)

    all_numbers = [f"{i:02d}" for i in range(100)]
    results = []

    for num in all_numbers:
        freq = counter_total.get(num, 0)
        recent_freq = counter_recent.get(num, 0)

        gan = 0
        for d in reversed(two_digits):
            if d != num:
                gan += 1
            else:
                break

        score = (freq*2.5)+(recent_freq*3)+(gan*1.2)

        results.append({
            "Số": num,
            "Tần suất": freq,
            "7 ngày": recent_freq,
            "Gan": gan,
            "Điểm AI": round(score,2)
        })

    df = pd.DataFrame(results)
    return df.sort_values(by="Điểm AI", ascending=False)

# ===== GIAO DIỆN =====
days = st.slider("Số ngày phân tích", 30, 120, 60)

if st.button("🚀 Chạy AI"):
    try:
        two_digits = fetch_data(days)
        result = ai_analysis(two_digits)

        st.subheader("🎯 TOP 12 SỐ AI")
        st.dataframe(result.head(12))
        st.bar_chart(result.head(10).set_index("Số"))

    except:
        st.error("Không lấy được dữ liệu, thử lại sau.")

