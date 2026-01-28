import streamlit as st
import pandas as pd
import requests
from collections import Counter
from datetime import datetime

st.set_page_config(page_title="AI Xổ Số PRO MAX", layout="wide")
st.title("🤖 AI TỰ ĐỘNG PHÂN TÍCH LÔ 2 SỐ TỪ GIẢI ĐẶC BIỆT")

# ================= LƯU LỊCH SỬ =================
if "history" not in st.session_state:
    st.session_state.history = []

# ================= HÀM LẤY DỮ LIỆU =================
def lay_du_lieu(mien, so_ngay):
    if mien == "Miền Bắc":
        url = "https://api.xoso.dev/v1/results/mb"
    else:
        url = "https://api.xoso.dev/v1/results/mn"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        results = []
        for item in data[:so_ngay]:
            db = item["specialPrize"]
            results.append(str(db)[-2:])

        return results
    except:
        return []

# ================= AI PHÂN TÍCH =================
def phan_tich_ai(two_digits):
    counter_total = Counter(two_digits)
    recent = two_digits[-7:]
    counter_recent = Counter(recent)

    all_numbers = [f"{i:02d}" for i in range(100)]
    results = []

    for num in all_numbers:
        freq = counter_total.get(num, 0)
        recent_freq = counter_recent.get(num, 0)

        # Gan
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

        # Chu kỳ tuần (5–8 ngày)
        week_cycle_score = 5 if 5 <= cycle_avg <= 8 else 0

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

# ================= GIAO DIỆN =================
st.subheader("⚙️ CÀI ĐẶT")

mien = st.radio("Chọn miền", ["Miền Bắc", "Miền Nam"])
so_ngay = st.slider("Phân tích bao nhiêu ngày gần nhất?", 30, 120, 60)

if st.button("🚀 CHẠY AI TỰ ĐỘNG"):

    with st.spinner("Đang lấy dữ liệu và phân tích..."):
        two_digits = lay_du_lieu(mien, so_ngay)

    if len(two_digits) < 20:
        st.error("Không lấy được dữ liệu. Thử lại sau.")
    else:
        df = phan_tich_ai(two_digits)

        st.subheader(f"📊 KẾT QUẢ AI — {mien}")
        st.dataframe(df)

        st.subheader("🎯 TOP 12 SỐ ĐỀ XUẤT")
        top12 = df.head(12)
        st.write(top12)

        st.subheader("📈 BIỂU ĐỒ XU HƯỚNG")
        st.bar_chart(df.head(10).set_index("Số"))

        # Lưu lịch sử
        st.session_state.history.append({
            "Thời gian": datetime.now().strftime("%d-%m %H:%M"),
            "Miền": mien,
            "Chu kỳ": so_ngay,
            "Top số": ", ".join(top12["Số"])
        })

# ================= LỊCH SỬ =================
st.subheader("📜 LỊCH SỬ PHÂN TÍCH")

if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history)
    st.dataframe(history_df)
else:
    st.write("Chưa có lịch sử.")
