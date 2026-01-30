import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime, timedelta

st.set_page_config(page_title="AI Xác Suất Lô 2 Số", layout="wide")

st.title("🎯 AI TÍNH XÁC SUẤT LÔ 2 SỐ NGÀY MAI")

st.markdown("Dán kết quả lô 2 số mỗi ngày (mỗi dòng = 1 ngày)")

raw = st.text_area("Nhập dữ liệu")

# ====== PHÂN TÍCH ======
def analyze(data_lines):
    days = []
    for line in data_lines:
        nums = [x.zfill(2) for x in line.split() if x.isdigit()]
        days.append(nums)

    today = datetime.now()
    tomorrow_weekday = (today.weekday() + 1) % 7

    flat = [n for day in days for n in day]
    total_freq = Counter(flat)

    last7 = [n for day in days[:7] for n in day]
    last7_freq = Counter(last7)

    # Gán ngày giả lập
    weekday_map = {}
    for i, day in enumerate(days):
        date = today - timedelta(days=i)
        weekday_map[i] = date.weekday()

    weekday_freq = Counter()
    for i, day in enumerate(days):
        if weekday_map[i] == tomorrow_weekday:
            for n in day:
                weekday_freq[n] += 1

    avg = np.mean(list(total_freq.values()))

    results = []
    all_nums = [f"{i:02d}" for i in range(100)]

    for num in all_nums:
        freq = total_freq.get(num, 0)
        recent = last7_freq.get(num, 0)
        week = weekday_freq.get(num, 0)

        # GAN
        gan = 0
        for day in days:
            if num not in day:
                gan += 1
            else:
                break

        # XÁC SUẤT AI
        score = (freq*2.2) + (recent*3.5) + (gan*1.5) + (week*2.5)

        # Chuẩn hoá thành %
        prob = score / (avg * 10) * 100

        results.append({
            "Số": num,
            "Tần suất": freq,
            "7 ngày": recent,
            "Cùng thứ ngày mai": week,
            "Gan": gan,
            "Xác suất AI (%)": round(prob, 2)
        })

    df = pd.DataFrame(results)
    return df.sort_values(by="Xác suất AI (%)", ascending=False)

# ====== CHẠY ======
if st.button("🚀 TÍNH XÁC SUẤT NGÀY MAI"):
    lines = [x.strip() for x in raw.split("\n") if x.strip()]
    
    if len(lines) < 15:
        st.warning("Cần ít nhất 15 ngày dữ liệu")
    else:
        result = analyze(lines)

        st.subheader("🔥 TOP 15 SỐ XÁC SUẤT CAO NHẤT")
        st.dataframe(result.head(15), use_container_width=True)
        st.bar_chart(result.head(10).set_index("Số")["Xác suất AI (%)"])

        st.subheader("💣 NHÓM GAN CAO (DỄ BẬT)")
        gan_df = result.sort_values(by="Gan", ascending=False).head(10)
        st.dataframe(gan_df, use_container_width=True)

        st.subheader("📊 PHÂN BỐ XÁC SUẤT")
        st.line_chart(result["Xác suất AI (%)"])
