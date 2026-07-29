import base64
import os

import streamlit as st

# ---------------------------------------------------------------------- #
# Ilustrasi hero halaman Beranda — gambar PNG asli (assets/hero_illustration.png),
# menggantikan ilustrasi SVG mannequin sebelumnya.
# ---------------------------------------------------------------------- #
_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
_HERO_ILLUSTRATION_PATH = os.path.join(_ASSETS_DIR, "hero_illustration.png")


@st.cache_data(show_spinner=False)
def _hero_illustration_b64() -> str:
    with open(_HERO_ILLUSTRATION_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _hero_illustration_html() -> str:
    return (
        f'<img src="data:image/png;base64,{_hero_illustration_b64()}" '
        f'alt="Ilustrasi FitSense — kaos dengan pita ukur dan jaringan AI" />'
    )


def _icon(name: str) -> str:
    """Ikon garis 24x24 (gaya feather-icon) untuk langkah cara-kerja & panduan."""
    icons = {
        # orang / input data tubuh
        "user": """<circle cx="12" cy="8" r="3.4" stroke-width="1.8"/>
            <path d="M5.5 20v-1.2A5.8 5.8 0 0 1 11.3 13h1.4a5.8 5.8 0 0 1 5.8 5.8V20" stroke-width="1.8"/>""",
        # corong / preprocessing
        "filter": """<path d="M4 4h16l-6.2 7.6V18l-3.6 2v-8.4z" stroke-width="1.8" stroke-linejoin="round"/>""",
        # jaringan model
        "network": """<circle cx="6" cy="6" r="2.1" stroke-width="1.7"/>
            <circle cx="18" cy="6" r="2.1" stroke-width="1.7"/>
            <circle cx="12" cy="18" r="2.1" stroke-width="1.7"/>
            <path d="M7.7 7.4 10.5 16.2M16.3 7.4 13.5 16.2M8.1 6h7.8" stroke-width="1.6"/>""",
        # kaos / hasil prediksi
        "shirt": """<path d="M8.5 3.5 4 7v4h3v9.5h10V11h3V7l-4.5-3.5-2 1.7h-3z" stroke-width="1.7" stroke-linejoin="round"/>""",
        # gantungan baju / kategori pakaian
        "hanger": """<circle cx="12" cy="4.3" r="1.3" stroke-width="1.6"/>
            <path d="M12 5.6v2" stroke-width="1.6"/>
            <path d="M12 7.6 3.5 14a1.7 1.7 0 0 0 1 3h15a1.7 1.7 0 0 0 1-3z" stroke-width="1.7" stroke-linejoin="round"/>
            <path d="M6 17h12" stroke-width="1.4" opacity="0.6"/>""",
        # penggaris / pengukuran tubuh
        "ruler": """<rect x="3" y="8" width="18" height="8" rx="1.5" stroke-width="1.7" transform="rotate(-8 12 12)"/>
            <path d="M6.3 8.6 7.1 11.4M9.7 7.7 10.5 10.5M13.1 6.8 13.9 9.6M16.5 5.9 17.3 8.7"
                  stroke-width="1.4" stroke-linecap="round"/>""",
        # tag / dipakai untuk (acara)
        "tag": """<path d="M20 13.2 12.8 20.4a2 2 0 0 1-2.8 0l-6.4-6.4a2 2 0 0 1-.6-1.4V5.5A1.5 1.5 0 0 1 4.5 4h7.1c.5 0 1 .2 1.4.6l6.4 6.4a2 2 0 0 1 .6 1.4c0 .5-.2 1-.6 1.4z" stroke-width="1.7" stroke-linejoin="round"/>
            <circle cx="8.2" cy="8.2" r="1.2" stroke-width="1.5"/>""",
        # klik / sparkle prediksi
        "click": """<path d="M5 4.5 12 21l2-7 7-2z" stroke-width="1.7" stroke-linejoin="round"/>""",
        # hasil / checklist
        "check": """<circle cx="12" cy="12" r="8.5" stroke-width="1.8"/>
            <path d="M8.3 12.3 10.8 15l5-6" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>""",
    }
    return f'<svg viewBox="0 0 24 24" fill="none" stroke-linecap="round" stroke-linejoin="round">{icons[name]}</svg>'


def _arrow_svg() -> str:
    return """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
        stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M13 6l6 6-6 6"/></svg>"""


def _clean(html: str) -> str:
    """Hapus leading whitespace tiap baris agar Markdown (CommonMark) tidak
    salah mengira baris ber-indentasi >=4 spasi sebagai code block, yang
    menyebabkan HTML tampil sebagai teks mentah alih-alih dirender."""
    return "\n".join(line.strip() for line in html.strip().splitlines())


def render():
    st.markdown(
        _clean(
            f"""
            <div class="fs-hero">
                <div class="fs-hero-flex">
                    <div class="fs-hero-text">
                        <div class="fs-hero-title">FitSense</div>
                        <p>
                            FitSense adalah aplikasi yang membantu memprediksi kesesuaian ukuran 
                            pakaian berdasarkan data pengukuran tubuh pengguna. Cukup masukkan data 
                            pengukuran tubuh dan ukuran pakaian yang ingin dicoba, kemudian sistem akan 
                            memberikan hasil prediksi apakah ukuran tersebut  <b>Pas</b>, <b>Terlalu Kecil</b> atau <b>Terlalu Besar</b>.
                        </p>
                    </div>
                    <div class="fs-hero-illustration">
                        {_hero_illustration_html()}
                    </div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------ #
    # Bagaimana FitSense Bekerja? — alur horizontal 4 langkah + ikon
    # ------------------------------------------------------------------ #
    flow_steps = [
        ("user", "#F4ECD8", "Input Karakteristik Tubuh"),
        ("filter", "#E9EBF3", "Preprocessing Data"),
        ("network", "#E3F0E7", "XGBoost Model"),
        ("shirt", "#F5E6E6", "Prediksi Ukuran Pakaian"),
    ]
    flow_html = '<div class="fs-flow">'
    for i, (icon_name, bg, label) in enumerate(flow_steps):
        flow_html += f"""
            <div class="fs-flow-step">
                <div class="fs-flow-icon" style="background:{bg};">{_icon(icon_name)}</div>
                <div class="fs-flow-label">{label}</div>
            </div>
        """
        if i < len(flow_steps) - 1:
            flow_html += f'<div class="fs-flow-arrow">{_arrow_svg()}</div>'
    flow_html += "</div>"

    st.markdown(
        _clean(
            f"""
            <div class="fs-card">
                <div class="fs-section-title">⚙️ Bagaimana FitSense Bekerja?</div>
                {flow_html}
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------ #
    # Panduan Penggunaan — stepper horizontal 5 langkah + ikon
    # ------------------------------------------------------------------ #
    guide_steps = [
        ("user", "#F4ECD8", "Isi Data Diri"),
        ("ruler", "#E9EBF3", "Masukkan Pengukuran Tubuh"),
        ("tag", "#E3F0E7", "Pilih Ukuran yang Ingin Dicoba"),
        ("click", "#F5E6E6", "Klik Prediksi Ukuran"),
        ("check", "#F4ECD8", "Lihat Hasil & Rekomendasi"),
    ]

    steps_html = '<div class="fs-guide-flow">'
    for i, (icon_name, bg, title) in enumerate(guide_steps):
        steps_html += f"""
            <div class="fs-guide-step">
                <div class="fs-guide-icon-wrap">
                    <div class="fs-guide-icon" style="background:{bg};">{_icon(icon_name)}</div>
                    <div class="fs-guide-num">{i + 1}</div>
                </div>
                <div class="fs-guide-title">{title}</div>
            </div>
        """
    steps_html += "</div>"

    st.markdown(
        _clean(
            f"""
            <div class="fs-card">
                <div class="fs-section-title">📋 Panduan Penggunaan</div>
                {steps_html}
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        _clean(
            """
            <div class="fs-card" style="text-align:center;">
                <div class="fs-section-title" style="justify-content:center;">✨ Kenapa FitSense?</div>
                <p style="color:#5B6478; max-width:700px; margin:0 auto;">
                    FitSense memprediksi ukuran pakaian berdasarkan karakteristik tubuh pengguna 
                    menggunakan model XGBoost yang dilatih dari data pengukuran tubuh. Dengan pendekatan ini, 
                    hasil prediksi tidak hanya mengacu pada tabel ukuran umum yang dapat berbeda di setiap merek.
                </p>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )
