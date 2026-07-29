import base64
import os

import streamlit as st

from utils.style import load_css
from utils.preprocessing import load_artifacts
from pages_content import beranda, prediksi, info_model

# ---------------------------------------------------------------------- #
# Ikon halaman (favicon) & brand (logo) — memakai gambar PNG asli di
# assets/brand_icon.png (bukan emoji lagi).
# ---------------------------------------------------------------------- #
_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
_BRAND_ICON_PATH = os.path.join(_ASSETS_DIR, "brand_icon.png")


@st.cache_data(show_spinner=False)
def _brand_icon_b64() -> str:
    with open(_BRAND_ICON_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


st.set_page_config(
    page_title="FitSense",
    page_icon=_BRAND_ICON_PATH,
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

BRAND_ICON_B64 = _brand_icon_b64()
PAGE_ICONS = {"ruler": "📏", "chart": "📊"}

# ---------------------------------------------------------------------- #
# Konfigurasi halaman & navigasi
# ---------------------------------------------------------------------- #
PAGES = [
    {"key": "beranda", "label": "Beranda", "icon": "home"},
    {"key": "prediksi", "label": "Prediksi Ukuran", "icon": "straighten"},
    {"key": "info", "label": "Informasi Model", "icon": "insights"},
]

if "fs_page" not in st.session_state:
    st.session_state["fs_page"] = "beranda"

# ---------------------------------------------------------------------- #
# Sidebar Navigasi
# ---------------------------------------------------------------------- #
with st.sidebar:
    st.markdown(
        f"""
        <div class="fs-sidebar-brand">
            <div class="fs-sidebar-brand-icon"><img src="data:image/png;base64,{BRAND_ICON_B64}" alt="FitSense" /></div>
            <div>
                <p class="fs-logo">FitSense</p>
                <p class="fs-tagline">Smart Clothing Size Predictor</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="fs-nav-label">Menu</p>', unsafe_allow_html=True)

    for page in PAGES:
        is_active = st.session_state["fs_page"] == page["key"]
        if st.button(
            page["label"],
            key=f"nav_{page['key']}",
            icon=f":material/{page['icon']}:",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            # Kalau pengguna berpindah MENINGGALKAN halaman Prediksi (mis. ke
            # Beranda / Informasi Model), reset state hasil prediksi supaya
            # ketika mereka kembali ke halaman Prediksi, tampilannya otomatis
            # kembali ke form kosong (bukan menampilkan hasil prediksi lama).
            if st.session_state["fs_page"] == "prediksi" and page["key"] != "prediksi":
                st.session_state["fs_show_result"] = False
                st.session_state.pop("fs_raw_input", None)
            st.session_state["fs_page"] = page["key"]
            st.rerun()

    st.markdown("---")

menu_key = st.session_state["fs_page"]

# ---------------------------------------------------------------------- #
# Load model & artefak (dengan penanganan error yang ramah pengguna)
# ---------------------------------------------------------------------- #
try:
    artifacts = load_artifacts()
    load_error = None
except Exception as e:  # noqa: BLE001
    artifacts = None
    load_error = str(e)


def _show_load_error():
    st.error(
        "⚠️ Model belum berhasil dimuat. Pastikan seluruh dependensi (terutama **xgboost** "
        "dan **scikit-learn**) sudah terpasang sesuai `requirements.txt`, dan folder `model/` "
        "berada di lokasi yang benar."
    )
    with st.expander("Detail error"):
        st.code(load_error or "Tidak diketahui")


def _page_header(icon_name: str, title: str, desc: str):
    emoji = PAGE_ICONS.get(icon_name, "✨")
    st.markdown(
        f"""
        <div class="fs-page-header">
            <div class="fs-page-header-icon"><span class="fs-brand-emoji">{emoji}</span></div>
            <div>
                <p class="fs-page-header-title">{title}</p>
                <p class="fs-page-header-desc">{desc}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------- #
# Routing halaman
# ---------------------------------------------------------------------- #
if menu_key == "beranda":
    beranda.render()

elif menu_key == "prediksi":
    _page_header("ruler", "Prediksi Ukuran", "Masukkan hasil ukur badanmu untuk mengetahui tingkat kecocokan ukuran.")
    if artifacts is None:
        _show_load_error()
    else:
        prediksi.render(artifacts)

elif menu_key == "info":
    _page_header("chart", "Informasi Model", "Detail performa dan interpretasi model XGBoost di balik FitSense.")
    if artifacts is None:
        _show_load_error()
    else:
        info_model.render(artifacts)
