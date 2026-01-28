import streamlit as st
import pandas as pd
from collections import Counter
from datetime import datetime

st.set_page_config(page_title="AI Xổ Số PRO MAX", layout="wide")

st.title("🤖 AI PHÂN TÍCH LÔ + CHU KỲ TUẦN")

if "history" not in st.session_state:
    st.session_state.history = []

mien = st.radio("Chọn miền:", ["Miền Bắc", "Miền Nam"])

data = st.text_area("Dán kết quả giải đặc biệt (mỗi dòng 1 số)")

def phan_tich_ai(two_digits):
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

        # Chu kỳ
        positions = [i for i, x in enumerate(two_digits) if x == num]
        if len(positions) > 1:
            cycles = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            cycle_avg = sum(cycles) / len(cycles)
        else:
            cycle_avg = len(two_digits)

        # Chu kỳ tuần (5–8 ngày)
        week_cycle_score = 0
        if 5 <= cycle_avg <= 8:
            week_cycle_score = 5

        score = (freq * 2.5) + (recent_freq * 3) + (gan * 1.2) + (10 / (cycle_avg + 1)) + week_cycle_score

        results.append({
            "Số": num,
            "Tần suất": freq,
            "7 ngày gần": recent_freq,
            "Gan": gan,
            "Chu kỳ TB": round(cycle_avg,2),
            "Điểm chu kỳ tuần": week_cycle_score,
            "Điểm AI": round(score,2)
        })

    df = pd.DataFrame(results)
    return df.sort_values(by="Điểm AI", ascending=False)


if st.button("🚀 CHẠY AI"):
    lines = data.strip().split("\n")
    two_digits = [line.strip()[-2:] for line in lines if line.strip().isdigit()]

    if len(two_digits) < 20:
        st.error("Cần ít nhất 20 ngày dữ liệu")
    else:
        df = phan_tich_ai(two_digits)

        st.subheader("🎯 TOP 12 SỐ AI ĐỀ XUẤT")
        st.write(df.head(12))

        st.bar_chart(df.head(10).set_index("Số"))

        # Lưu lịch sử
        st.session_state.history.append({
            "Thời gian": datetime.now().strftime("%d-%m %H:%M"),
            "Miền": mien,
            "Top số": ", ".join(df.head(5)["Số"])
        })

st.subheader("📜 LỊCH SỬ PHÂN TÍCH")
if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history)
    st.dataframe(history_df)
else:
    st.write("Chưa có dữ liệu lịch sử.")
