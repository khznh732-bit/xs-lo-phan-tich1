import streamlit as st
import pandas as pd
from collections import Counter

st.title("🤖 AI PRO Phân Tích Lô 2 Số")

st.write("Dán kết quả giải đặc biệt (mỗi dòng 1 số)")

input_data = st.text_area("Ví dụ:\n843921\n12058\n77634\n99012")

if st.button("Chạy AI PRO"):

    lines = input_data.strip().split("\n")
    two_digits = [line.strip()[-2:] for line in lines if line.strip().isdigit()]

    if len(two_digits) < 15:
        st.warning("Cần ít nhất 15 ngày dữ liệu")
        st.stop()

    counter_total = Counter(two_digits)
    recent = two_digits[-7:]
    counter_recent = Counter(recent)

    all_numbers = [f"{i:02d}" for i in range(100)]
    results = []

    for num in all_numbers:
        freq = counter_total.get(num, 0)
        recent_freq = counter_recent.get(num, 0)

        # Tính gan
        gan = 0
        for d in reversed(two_digits):
            if d != num:
                gan += 1
            else:
                break

        # Chu kỳ trung bình
        positions = [i for i, x in enumerate(two_digits) if x == num]
        if len(positions) > 1:
            cycles = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            cycle_avg = sum(cycles) / len(cycles)
        else:
            cycle_avg = len(two_digits)

        # AI Score ổn định
        score = (freq * 2.5) + (recent_freq * 3) + (gan * 1.2) + (10 / (cycle_avg + 1))

        results.append({
            "Số": num,
            "Tần suất": freq,
            "7 ngày gần": recent_freq,
            "Gan": gan,
            "Chu kỳ TB": round(cycle_avg,2),
            "Điểm AI": round(score,2)
        })

    df = pd.DataFrame(results)

    st.subheader("📊 Bảng phân tích AI")
    st.dataframe(df.sort_values(by="Điểm AI", ascending=False))

    st.subheader("🎯 TOP 12 SỐ AI ĐỀ XUẤT")
    st.write(df.sort_values(by="Điểm AI", ascending=False).head(12))

    st.bar_chart(df.sort_values(by="Điểm AI", ascending=False).head(10).set_index("Số"))
