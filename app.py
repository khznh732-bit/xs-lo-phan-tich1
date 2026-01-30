import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime, timedelta

st.set_page_config(page_title="AI Lô 2 Số", layout="wide")
st.title("🎯 AI XÁC SUẤT LÔ 2 SỐ NGÀY MAI")

st.markdown("Upload Excel hoặc nhập tay. File phải có cột **Lô**")

data_lines = []

# ===== UPLOAD FILE AN TOÀN =====
uploaded = st.file_uploader("📂 Tải file Excel/CSV", type=["xlsx", "csv"])

if uploaded:
    try:
        if uploaded.name.endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded, engine="openpyxl")

        st.success("Đọc file thành công")

        df.columns = df.columns.str.strip()

        if "Lô" not in df.columns:
            st.error("File phải có cột tên: Lô")
        else:
            data_lines = df["Lô"].astype(str).tolist()

    except Exception as e:
        st.error(f"Lỗi đọc file: {e}")

# ===== NHẬP TAY =====
if not data_lines:
    raw = st.text_area("Hoặc dán dữ liệu mỗi dòng là 1 ngày")
    if raw:
        data_lines = [x.strip() for x in raw.split("\n") if x.strip()]

# ===== PHÂN TÍCH =====
def analyze(days):
    parsed = []
    for line in days:
        nums = [x.zfill(2) for x in line.split() if x.isdigit()]
        parsed.append(nums)

    if not parsed:
        return None

    today = datetime.now()
    tomorrow_weekday = (today.weekday() + 1) % 7

    flat = [n for day in parsed for n in day]
    total_freq = Counter(flat)

    last7 = [n for day in parsed[:7] for n in day]
    last7_freq = Counter(last7)

    weekday_freq = Counter()
    for i, day in enumerate(parsed):
        date = today - timedelta(days=i)
        if date.weekday() == tomorrow_weekday:
            for n in day:
                weekday_freq[n] += 1

    avg = np.mean(list(total_freq.values())) if total_freq else 1

    results = []
    all_nums = [f"{i:02d}" for i in range(100)]

    for num in all_nums:
        freq = total_freq.get(num, 0)
        recent = last7_freq.get(num, 0)
        week = weekday_freq.get(num, 0)

        gan = 0
        for day in parsed:
            if num not in day:
                gan += 1
            else:
                break

        score = (freq*2.2) + (recent*3.5) + (gan*1.5) + (week*2.5)
        prob = (score / (avg * 10)) * 100

        results.append({
            "Số": num,
            "Tần suất": freq,
            "7 ngày": recent,
            "Cùng thứ mai": week,
            "Gan": gan,
            "Xác suất AI (%)": round(prob, 2)
        })

    return pd.DataFrame(results).sort_values(by="Xác suất AI (%)", ascending=False)

# ===== CHẠY =====
if st.button("🚀 TÍNH XÁC SUẤT"):
    if len(data_lines) < 10:
        st.warning("Cần ít nhất 10 ngày dữ liệu")
    else:
        result = analyze(data_lines)

        if result is None:
            st.error("Dữ liệu không hợp lệ")
        else:
            st.subheader("🔥 TOP 15")
            st.dataframe(result.head(15), use_container_width=True)
            st.bar_chart(result.head(10).set_index("Số")["Xác suất AI (%)"])

            st.subheader("💣 SỐ GAN CAO")
            st.dataframe(result.sort_values(by="Gan", ascending=False).head(10))
