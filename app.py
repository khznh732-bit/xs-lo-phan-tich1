import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
from sklearn.ensemble import RandomForestClassifier

st.title("🤖 AI PRO Dự Đoán Lô 2 Số Từ Giải Đặc Biệt")

st.write("Dán danh sách giải đặc biệt (mỗi dòng 1 kết quả)")

input_data = st.text_area("Ví dụ:\n843921\n12058\n77634\n99012")

if st.button("Chạy AI PRO"):

    lines = input_data.strip().split("\n")
    two_digits = [line.strip()[-2:] for line in lines if line.strip().isdigit()]

    if len(two_digits) < 20:
        st.warning("Cần ít nhất 20 ngày dữ liệu")
        st.stop()

    all_numbers = [f"{i:02d}" for i in range(100)]

    # ===== TẠO FEATURE =====
    X = []
    y = []

    for i in range(10, len(two_digits)-1):
        past = two_digits[:i]
        next_num = two_digits[i]

        counter_total = Counter(past)
        recent = past[-7:]
        counter_recent = Counter(recent)

        features = []
        for num in all_numbers:
            freq = counter_total.get(num, 0)
            recent_freq = counter_recent.get(num, 0)

            gan = 0
            for d in reversed(past):
                if d != num:
                    gan += 1
                else:
                    break

            features.append([freq, recent_freq, gan])

        # nhãn: số xuất hiện ngày tiếp theo
        label = all_numbers.index(next_num)

        X.append(features)
        y.append(label)

    X = np.array(X)
    y = np.array(y)

    # reshape cho ML
    X = X.reshape(len(X), -1)

    # ===== TRAIN AI =====
    model = RandomForestClassifier(n_estimators=200)
    model.fit(X, y)

    # ===== DỰ ĐOÁN NGÀY TIẾP =====
    counter_total = Counter(two_digits)
    recent = two_digits[-7:]
    counter_recent = Counter(recent)

    features = []
    for num in all_numbers:
        freq = counter_total.get(num, 0)
        recent_freq = counter_recent.get(num, 0)

        gan = 0
        for d in reversed(two_digits):
            if d != num:
                gan += 1
            else:
                break

        features.append([freq, recent_freq, gan])

    X_pred = np.array(features).reshape(1, -1)

    probs = model.predict_proba(X_pred)[0]

    results = pd.DataFrame({
        "Số": all_numbers,
        "Xác suất AI": probs
    }).sort_values(by="Xác suất AI", ascending=False)

    st.subheader("🎯 TOP 15 SỐ AI ĐỀ XUẤT")
    st.dataframe(results.head(15))

    st.bar_chart(results.set_index("Số").head(10))
