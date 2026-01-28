import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

st.set_page_config(page_title="Phân tích Lô 2 số", layout="centered")

st.title("🎯 PHÂN TÍCH LÔ 2 SỐ TỪ GIẢI ĐẶC BIỆT")

# ===================== LẤY DỮ LIỆU =====================
@st.cache_data
def fetch_data(days):
    url = "https://xskt.com.vn/xsmb"
    html = requests.get(url, timeout=10).text

    db_numbers = re.findall(r'ĐB</td><td.*?>(\d{5})', html)
    lo_2_so = [n[-2:] for n in db_numbers]

    dates = [datetime.today() - timedelta(days=i) for i in range(len(lo_2_so))]
    df = pd.DataFrame({"date": dates, "lo": lo_2_so})

    cutoff = datetime.today() - timedelta(days=days)
    return df[df["date"] >= cutoff]

# ===================== GIAO DIỆN =====================
days = st.slider("Chọn số ngày phân tích", 30, 365, 90)

if st.button("📥 CẬP NHẬT DỮ LIỆU"):
    st.session_state["data"] = fetch_data(days)
    st.success("Đã cập nhật dữ liệu")

if "data" in st.session_state:
    df = st.session_state["data"]

    st.subheader("📊 THỐNG KÊ")

    freq = df["lo"].value_counts().reset_index()
    freq.columns = ["lo", "frequency"]

    all_lo = pd.DataFrame({"lo": [f"{i:02d}" for i in range(100)]})
    stats = all_lo.merge(freq, on="lo", how="left").fillna(0)

    # Tính gan thật
    gan_list = []
    for lo in stats["lo"]:
        if lo in df["lo"].values:
            last_date = df[df["lo"] == lo]["date"].max()
            gan = (datetime.today() - last_date).days
        else:
            gan = days
        gan_list.append(gan)

    stats["gan"] = gan_list
    stats["score"] = stats["frequency"] * 0.5 + stats["gan"] * 0.5

    # TOP số đáng chú ý
    st.write("🔥 TOP LÔ ĐÁNG CHÚ Ý")
    st.dataframe(stats.sort_values("score", ascending=False).head(10), use_container_width=True)

    # Lô không về
    st.write("❄️ LÔ KHÔNG VỀ")
    st.dataframe(stats[stats["frequency"] == 0], use_container_width=True)

    # Lô rơi (xuất hiện liên tiếp)
    st.write("🔁 LÔ RƠI")
    df_sorted = df.sort_values("date")
    df_sorted["prev"] = df_sorted["lo"].shift(1)
    roi = df_sorted[df_sorted["lo"] == df_sorted["prev"]]["lo"].unique()
    st.write(list(roi))

    # Biểu đồ gan
    st.write("📈 BIỂU ĐỒ GAN CAO NHẤT")
    top_gan = stats.sort_values("gan", ascending=False).head(10)

    fig, ax = plt.subplots()
    ax.bar(top_gan["lo"], top_gan["gan"])
    ax.set_ylabel("Số ngày chưa ra")
    ax.set_xlabel("Lô")
    st.pyplot(fig)

else:
    st.info("👉 Bấm 'CẬP NHẬT DỮ LIỆU' để bắt đầu")
