import streamlit as st
import pandas as pd
from collections import Counter

st.title("📊 Phân Tích Lô Theo Giải Đặc Biệt")

st.write("Nhập danh sách giải đặc biệt các ngày gần đây (mỗi dòng 1 kết quả)")

input_data = st.text_area("Ví dụ:\n843921\n12058\n77634\n99012")

if st.button("Phân tích"):
    lines = input_data.strip().split("\n")

    # Lấy 2 số cuối
    two_digits = [line.strip()[-2:] for line in lines if line.strip().isdigit()]

    if len(two_digits) == 0:
        st.warning("Không có dữ liệu hợp lệ")
        st.stop()

    counter = Counter(two_digits)

    all_numbers = [f"{i:02d}" for i in range(100)]

    results = []

    for num in all_numbers:
        count = counter.get(num, 0)

        # Tính gan (bao nhiêu ngày chưa xuất hiện)
        gan = 0
        for d in reversed(two_digits):
            if d != num:
                gan += 1
            else:
                break

        results.append({
            "Số": num,
            "Số lần về": count,
            "Gan (ngày chưa về)": gan
        })

    df = pd.DataFrame(results)

    st.subheader("📋 Bảng thống kê")
    st.dataframe(df.sort_values(by="Số lần về", ascending=False))

    st.subheader("🔥 Top 10 số ra nhiều nhất")
    st.write(df.sort_values(by="Số lần về", ascending=False).head(10))

    st.subheader("📈 Top 10 số gan cao nhất")
    st.write(df.sort_values(by="Gan (ngày chưa về)", ascending=False).head(10))
