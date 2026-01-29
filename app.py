import streamlit as st
import pandas as pd
from collections import Counter
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="AI Lô Chu Kỳ Tuần", layout="wide")

st.title("🤖 AI PHÂN TÍCH LÔ + CHU KỲ TUẦN")

# ================= NHẬP DỮ LIỆU =================
st.subheader("📥 Dán kết quả giải đặc biệt (mỗi dòng 1 số)")

raw_data = st.text_area("Ví dụ:\n12345\n67890\n11223")

if "history" not in st.session_state:
    st.session_state.history = []

# ================= HÀM PHÂN TÍCH =================
def analyze(numbers):
    df = pd.DataFrame({"special": numbers})
    df["two"] = df["special"].str[-2:]

    # Ngày giả lập (lùi dần)
    today = datetime.now()
    df["date"] = [today - timedelta(days=i) for i in range(len(df))]
    df["weekday"] = df["date"].dt.weekday

    two_list = df["two"].tolist()

    total_freq = Counter(two_list)
    last7_freq = Counter(two_list[:7])
    today_w = datetime.now().weekday()
    weekday_freq = Counter(df[df["weekday"] == today_w]["two"])

    avg = np.mean(list(total_freq.values()))

    results = []
    all_nums = [f"{i:02d}" for i in range(100)]

    for num in all_nums:
        freq = total_freq.get(num, 0)
        recent = last7_freq.get(num, 0)
        week = weekday_freq.get(num, 0)

        # GAN
        gan = 0
        for n in two_list:
            if n != num:
                gan += 1
            else:
                break

        # BẤT THƯỜNG = SẮP NỔ
        anomaly = (gan > avg*2) or (recent == 0 and freq > avg)

        score = (freq*2.5) + (recent*3) + (gan*1.3) + (week*2)
        if anomaly:
            score *= 1.5

        results.append({
            "Số": num,
            "Tần suất": freq,
            "7 ngày": recent,
            "Cùng thứ hôm nay": week,
            "Gan": gan,
            "🔥 Sắp nổ": "⚠️" if anomaly else "",
            "Điểm AI": round(score, 2)
        })

    return pd.DataFrame(results).sort_values(by="Điểm AI", ascending=False)

# ================= CHẠY AI =================
if st.button("🚀 CHẠY AI"):
    nums = [x.strip() for x in raw_data.split("\n") if x.strip().isdigit() and len(x.strip()) == 5]

    if len(nums) < 10:
        st.warning("Cần ít nhất 10 ngày dữ liệu")
    else:
        result = analyze(nums)

        st.subheader("🎯 TOP 12 AI")
        st.dataframe(result.head(12), use_container_width=True)
        st.bar_chart(result.head(10).set_index("Số")["Điểm AI"])

        st.subheader("🔥 NHÓM SỐ CÓ DẤU HIỆU SẮP NỔ")
        hot = result[result["🔥 Sắp nổ"] == "⚠️"].head(6)
        if not hot.empty:
            st.dataframe(hot, use_container_width=True)
        else:
            st.write("Chưa có số bất thường mạnh")

        st.session_state.history.append(result.head(5))

# ================= LỊCH SỬ =================
st.subheader("📜 LỊCH SỬ PHÂN TÍCH")
if st.session_state.history:
    for i, h in enumerate(st.session_state.history[::-1]):
        st.write(f"Lần {len(st.session_state.history)-i}")
        st.dataframe(h, use_container_width=True)
else:
    st.write("Chưa có dữ liệu lịch sử")
