import streamlit as st
import pandas as pd
import requests
from collections import Counter
from datetime import datetime

st.set_page_config(page_title="AI Xổ Số TỰ ĐỘNG", layout="wide")
st.title("🤖 AI PHÂN TÍCH GIẢI ĐẶC BIỆT – TỰ ĐỘNG 100%")

if "history" not in st.session_state:
    st.session_state.history = []

# ======= API TỰ ĐỘNG =======
@st.cache_data(ttl=3600)
def fetch_data(days):
    try:
        url = "https://api.xoso.dev/v1/mb/results"   # API mở
        r = requests.get(url, timeout=10)
        data = r.json()["data"][:days]

        df = pd.DataFrame(data)
        df["special"] = df["giai_dac_biet"]
        df["two"] = df["special"].astype(str).str[-2:]
        return df

    except:
        return None

# ======= AI =======
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

        positions = [i for i, x in enumerate(two_digits) if x == num]
        if len(positions) > 1:
            cycles = [positions[i+1]-positions[i] for i in range(len(positions)-1)]
            cycle_avg = sum(cycles)/len(cycles)
        else:
            cycle_avg = len(two_digits)

        score = (freq*2.5)+(recent_freq*3)+(gan*1.2)+(10/(cycle_avg+1))

        results.append({
            "Số": num,
            "Tần suất": freq,
            "7 ngày": recent_freq,
            "Gan": gan,
            "Chu kỳ TB": round(cycle_avg,2),
            "Điểm AI": round(score,2)
        })

    df = pd.DataFrame(results)
    return df.sort_values(by="Điểm AI", ascending=False)

# ======= UI =======
st.subheader("⚙️ CÀI ĐẶT")
days = st.slider("Phân tích bao nhiêu ngày gần nhất?", 30, 200, 90)

if st.button("🚀 CHẠY AI TỰ ĐỘNG"):
    df_data = fetch_data(days)

    if df_data is None:
        st.error("Không lấy được dữ liệu. Thử lại sau.")
    else:
        two_digits = df_data["two"].tolist()
        result_df = ai_analysis(two_digits)

        st.subheader("🎯 TOP 12 AI ĐỀ XUẤT")
        top12 = result_df.head(12)
        st.dataframe(top12)
        st.bar_chart(result_df.head(10).set_index("Số"))

        st.session_state.history.append({
            "Thời gian": datetime.now().strftime("%d-%m %H:%M"),
            "Top số": ", ".join(top12["Số"])
        })

# ======= LỊCH SỬ =======
st.subheader("📜 LỊCH SỬ PHÂN TÍCH")
if st.session_state.history:
    st.dataframe(pd.DataFrame(st.session_state.history))
else:
    st.write("Chưa có lịch sử.")
