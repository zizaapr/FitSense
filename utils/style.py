"""
style.py
--------
Tema visual FitSense: "kartu tag ukur penjahit" (tailor's measuring tag).

Konsep: tinta navy (seperti bolpoin penjahit menandai pola) dipadukan dengan
emas kuningan (seperti jarum/kancing kuningan & benang emas), tipografi serif
Fraunces untuk judul (kesan label butik/atelier), dan IBM Plex Mono untuk
semua angka & ukuran (kesan pita ukur / penggaris). Elemen "tag pakaian"
(gantungan berlubang, jahitan putus-putus) dipakai untuk badge hasil
prediksi supaya terasa seperti tag baju asli, bukan badge SaaS generik.

Dipakai konsisten di ketiga halaman, tetap terbaca meski Chrome/OS pengguna
diset ke dark mode, dan responsif di layar kecil.
"""

import streamlit as st

# ---------------------------------------------------------------------- #
# Palet warna
# ---------------------------------------------------------------------- #
INK = "#1B2A4A"             # navy ink — warna teks utama & tinta penjahit
INK_DARK = "#0E1830"
INK_SOFT = "#E9EBF3"        # tint navy sangat lembut (bg ikon dsb.)
BRASS = "#A9821F"           # emas kuningan — aksen utama (kancing/jarum)
BRASS_DARK = "#7C5F16"
BRASS_LIGHT = "#D8B25C"
BRASS_SOFT = "#F4ECD8"      # tint kuningan lembut
BG = "#F6F2E7"              # kertas krem hangat (kain/kertas pola)
SURFACE = "#FFFEFA"
TEXT = INK
MUTED = "#5B6478"
BORDER = "#E3DBC6"          # garis warna kain/kertas hangat
PAS = "#3E7D5A"             # benang hijau -> pas
KECIL = "#B14D3D"           # benang merah bata -> kekecilan
BESAR = "#2E6E93"           # benang biru -> kebesaran

STATUS_COLORS = {"Pas": PAS, "Terlalu Kecil": KECIL, "Terlalu Besar": BESAR}


def load_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700;9..144,800&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600;700&display=swap');

        /* =====================================================================
           FIX: kunci halaman ke color-scheme terang.
           ===================================================================== */
        :root, html {{
            color-scheme: light only;
            --fs-ink: {INK};
            --fs-ink-dark: {INK_DARK};
            --fs-brass: {BRASS};
            --fs-brass-light: {BRASS_LIGHT};
            --fs-border: {BORDER};
        }}

        html, body, [class*="css"] {{
            font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            color: {TEXT} !important;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        h1, h2, h3, h4, .fs-heading {{
            font-family: 'Fraunces', Georgia, serif !important;
            font-optical-sizing: auto;
            letter-spacing: -0.01em;
            color: {TEXT} !important;
        }}

        /* Angka & ukuran selalu memakai monospace ala pita ukur */
        .fs-mono, .fs-info-pill-value, .fs-proba-card-pct,
        [data-testid="stMetricValue"],
        [data-testid="stNumberInput"] input {{
            font-family: 'IBM Plex Mono', 'Courier New', monospace !important;
        }}

        /* Latar aplikasi: kertas krem hangat + jejak halus, bukan gradasi ungu SaaS */
        .stApp {{
            background:
                radial-gradient(900px 420px at 90% -6%, rgba(169,130,31,0.10) 0%, rgba(169,130,31,0) 58%),
                radial-gradient(760px 380px at -8% 8%, rgba(27,42,74,0.06) 0%, rgba(27,42,74,0) 55%),
                linear-gradient(180deg, {BG} 0%, #F1ECDC 100%);
            background-attachment: fixed;
        }}

        ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(180deg, {BRASS_LIGHT}, {BRASS});
            border-radius: 999px;
            border: 2px solid {BG};
        }}

        @keyframes fsFadeUp {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        .fs-hero, .fs-card, div[data-testid="stForm"] {{
            animation: fsFadeUp 0.45s ease both;
        }}

        p, span, li, label, .stMarkdown, .stCaption,
        [data-testid="stMarkdownContainer"],
        [data-testid="stWidgetLabel"] p,
        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"],
        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] p,
        [data-testid="stForm"] label,
        [data-testid="stCaptionContainer"] {{
            color: {TEXT} !important;
        }}
        [data-testid="stCaptionContainer"] {{
            color: {MUTED} !important;
        }}

        [data-testid="stExpander"] {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(27,42,74,0.05);
        }}
        [data-testid="stExpander"] summary {{
            font-weight: 600;
            border-radius: 16px;
        }}
        [data-testid="stDataFrame"] {{
            border: 1px solid {BORDER};
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 4px 14px rgba(27,42,74,0.05);
        }}

        [data-testid="stNumberInput"] input,
        [data-testid="stTextInput"] input,
        div[data-baseweb="select"] > div {{
            border-radius: 10px !important;
            border-color: {BORDER} !important;
        }}

        /* Streamlit menampilkan hint "Press Enter to submit form" sebagai
           lapisan absolute yang menumpuk DI ATAS teks input (bukan di bawah
           kotaknya) begitu field dianggap "dirty". Di kolom sempit (grid 2-3
           kolom pada form pengukuran), hint ini bertabrakan langsung dengan
           angka yang sedang diketik pengguna. Formulir di sini sudah punya
           tombol submit ("Prediksi Ukuran") yang jelas, jadi hint ini
           disembunyikan saja supaya angka yang diketik tetap terbaca. */
        [data-testid="InputInstructions"] {{
            display: none !important;
        }}
        div[data-baseweb="select"] > div:focus-within,
        [data-testid="stNumberInput"] input:focus,
        [data-testid="stTextInput"] input:focus {{
            border-color: {BRASS} !important;
            box-shadow: 0 0 0 3px rgba(169,130,31,0.16) !important;
        }}

        a {{ color: {BRASS_DARK} !important; }}

        /* =====================================================================
           SIDEBAR
           ===================================================================== */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #FFFEFA 0%, #FBF8F0 100%);
            border-right: 1px solid {BORDER};
            text-align: left !important;
        }}
        section[data-testid="stSidebar"] * {{
            color: {TEXT};
        }}
        /* Pastikan seluruh isi sidebar rata kiri, bukan rata tengah.
           Streamlit membungkus konten sidebar dengan beberapa lapis testid
           berbeda tergantung versi (stSidebarUserContent, stVerticalBlock,
           dst.) — semuanya dipaksa rata kiri di sini supaya konsisten. */
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
        section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"],
        section[data-testid="stSidebar"] [data-testid="stElementContainer"],
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            align-items: flex-start !important;
            text-align: left !important;
            justify-content: flex-start !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
            color: {MUTED} !important;
        }}

        .fs-sidebar-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 0.3rem 0 1.2rem 0;
            border-bottom: 1px dashed {BORDER};
            margin-bottom: 1rem;
        }}
        .fs-sidebar-brand-icon {{
            width: 42px;
            height: 42px;
            border-radius: 11px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            box-shadow: 0 6px 16px rgba(14,24,48,0.32), inset 0 0 0 1.5px rgba(216,178,92,0.55);
        }}
        .fs-sidebar-brand-icon img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }}
        /* Ikon emoji (header halaman) — dipakai untuk ikon per-halaman
           (ruler/chart) yang tetap memakai emoji. */
        .fs-brand-emoji {{
            font-size: 1.2rem;
            line-height: 1;
            filter: none;
        }}
        .fs-logo {{
            font-family: 'Fraunces', Georgia, serif;
            font-weight: 700;
            font-size: 1.35rem;
            line-height: 1.1;
            margin: 0;
            color: {INK} !important;
        }}
        .fs-tagline {{
            color: {MUTED} !important;
            font-size: 0.74rem;
            margin: 0;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }}

        .fs-nav-label {{
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            color: {BRASS_DARK} !important;
            text-transform: uppercase;
            margin: 0.2rem 0 0.6rem 2px;
        }}

        section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div[data-testid="stButton"] {{
            margin-bottom: 4px;
        }}

        /* Tombol menu sidebar. Streamlit menandai tombol dengan atribut
           `kind="secondary|primary"` di versi lama, dan dengan
           `data-testid="stBaseButton-secondary|primary"` di versi baru —
           kedua selector disertakan sekaligus supaya tetap konsisten di
           versi Streamlit apa pun. `justify-content` dipaksa `flex-start`
           dengan !important karena Streamlit kadang menengahkan konten
           tombol full-width secara default. */
        section[data-testid="stSidebar"] .stButton>button,
        section[data-testid="stSidebar"] [data-testid^="stBaseButton-"] {{
            width: 100%;
            display: flex !important;
            justify-content: flex-start !important;
            align-items: center !important;
            text-align: left !important;
            gap: 10px;
            font-family: 'IBM Plex Sans', sans-serif;
            font-weight: 600;
            font-size: 0.92rem;
            border-radius: 10px;
            padding: 0.6rem 0.9rem;
            border: 1px solid transparent;
            transition: background 0.15s ease, color 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
        }}
        section[data-testid="stSidebar"] .stButton>button p,
        section[data-testid="stSidebar"] [data-testid^="stBaseButton-"] p {{
            text-align: left !important;
            justify-content: flex-start !important;
        }}

        /* Tombol tidak aktif (secondary) */
        section[data-testid="stSidebar"] .stButton>button[kind="secondary"],
        section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {{
            background: transparent !important;
            color: {TEXT} !important;
        }}
        section[data-testid="stSidebar"] .stButton>button[kind="secondary"] *,
        section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] * {{
            color: {TEXT} !important;
            fill: {TEXT} !important;
        }}
        section[data-testid="stSidebar"] .stButton>button[kind="secondary"]:hover,
        section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {{
            background: {BRASS_SOFT} !important;
            border-color: {BRASS_SOFT} !important;
            transform: translateX(2px);
        }}
        section[data-testid="stSidebar"] .stButton>button[kind="secondary"]:hover *,
        section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover * {{
            color: {BRASS_DARK} !important;
            fill: {BRASS_DARK} !important;
        }}

        /* Tombol halaman aktif (primary) — ini yang sebelumnya membuat
           ikon & tulisan "hilang" karena warnanya tidak ikut terpaksa ke
           semua elemen anak (ikon material, teks) di versi Streamlit baru. */
        section[data-testid="stSidebar"] .stButton>button[kind="primary"],
        section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {{
            position: relative;
            background: linear-gradient(135deg, {INK} 0%, {INK_DARK} 100%) !important;
            border-color: {INK_DARK} !important;
            color: {BRASS_LIGHT} !important;
            box-shadow: 0 8px 18px rgba(14,24,48,0.30);
        }}
        /* Aksen kecil di sisi kiri tombol menu aktif, seperti penanda
           halaman pada tag baju — memperjelas menu mana yang sedang dibuka. */
        section[data-testid="stSidebar"] .stButton>button[kind="primary"]::before,
        section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]::before {{
            content: "";
            position: absolute;
            left: 0; top: 6px; bottom: 6px;
            width: 3px;
            border-radius: 3px;
            background: {BRASS_LIGHT};
        }}
        section[data-testid="stSidebar"] .stButton>button[kind="primary"] *,
        section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] * {{
            color: {BRASS_LIGHT} !important;
            fill: {BRASS_LIGHT} !important;
        }}

        section[data-testid="stSidebar"] hr {{
            margin: 1rem 0;
            border-color: {BORDER};
        }}
        .fs-sidebar-footer {{
            font-size: 0.72rem;
            font-family: 'IBM Plex Mono', monospace;
            color: {MUTED} !important;
            line-height: 1.5;
            padding: 0.6rem 0.7rem;
            background: {BG};
            border-radius: 10px;
            border: 1px dashed {BORDER};
        }}

        /* ---- Card umum: kesan "swatch kain" dengan jahitan tepi ---- */
        .fs-card {{
            position: relative;
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 1.7rem 1.9rem;
            box-shadow: 0 10px 26px rgba(27,42,74,0.07);
            margin-bottom: 1.3rem;
            transition: box-shadow 0.2s ease;
        }}
        .fs-card::before {{
            content: "";
            position: absolute;
            inset: 7px;
            border: 1.4px dashed rgba(169,130,31,0.28);
            border-radius: 11px;
            pointer-events: none;
        }}
        .fs-card:hover {{
            box-shadow: 0 14px 32px rgba(27,42,74,0.11);
        }}
        .fs-card h3, .fs-card h4 {{ margin-top: 0; }}

        .fs-section-title {{
            font-family: 'Fraunces', Georgia, serif;
            font-weight: 700;
            font-size: 1.12rem;
            color: {INK} !important;
            margin-bottom: 0.9rem;
            padding-bottom: 0.6rem;
            border-bottom: 1px solid {BORDER};
            display: flex;
            align-items: center;
            gap: 0.55rem;
        }}

        .fs-divider {{
            height: 1px;
            background: repeating-linear-gradient(90deg, {BORDER} 0 6px, transparent 6px 11px);
            margin: 1.1rem 0;
            border: none;
        }}

        .fs-page-header {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 1.4rem;
            padding-bottom: 1.1rem;
            border-bottom: 1px dashed {BORDER};
        }}
        .fs-page-header-icon {{
            width: 48px;
            height: 48px;
            border-radius: 13px;
            background: linear-gradient(135deg, {BRASS_SOFT} 0%, #EFE1BC 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            box-shadow: inset 0 0 0 1.5px rgba(169,130,31,0.35);
        }}
        .fs-page-header-title {{
            font-family: 'Fraunces', Georgia, serif;
            font-weight: 700;
            font-size: 1.5rem;
            color: {TEXT} !important;
            margin: 0;
        }}
        .fs-page-header-desc {{
            color: {MUTED} !important;
            font-size: 0.92rem;
            margin: 0;
        }}

        /* ---- Hero (Beranda): panel "tag ukuran besar" ---- */
        .fs-hero {{
            position: relative;
            background: linear-gradient(135deg, {INK_DARK} 0%, {INK} 55%, #223760 100%);
            border-radius: 20px;
            padding: 2.8rem 2.4rem;
            color: white;
            margin-bottom: 1.7rem;
            box-shadow: 0 18px 38px rgba(14,24,48,0.32);
            overflow: hidden;
            border: 1px solid rgba(216,178,92,0.35);
        }}
        .fs-hero::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 0;
            border-top: 3px dashed rgba(216,178,92,0.45);
        }}
        .fs-hero::after {{
            content: "";
            position: absolute;
            bottom: -90px; right: 90px;
            width: 200px; height: 200px;
            border-radius: 50%;
            background: rgba(216,178,92,0.10);
        }}
        .fs-hero > * {{ position: relative; z-index: 1; }}
        /* Judul hero pakai class sendiri (bukan <h1>) supaya tidak pernah
           kena timpa oleh aturan warna umum "h1, h2, h3, h4" di atas —
           itulah sebab tulisan "FitSense" sempat tidak kelihatan
           (tenggelam jadi navy-di-atas-navy). */
        .fs-hero-title {{
            color: #FFFFFF !important;
            font-family: 'Fraunces', Georgia, serif !important;
            font-weight: 800;
            font-size: 2.3rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .fs-hero p {{
            color: rgba(255,255,255,0.90) !important;
            font-size: 1.02rem;
            max-width: 660px;
            margin-bottom: 0;
            line-height: 1.6;
        }}

        /* ---- Hero: layout dua kolom (teks + ilustrasi pakaian) ---- */
        .fs-hero-flex {{
            display: flex;
            align-items: center;
            gap: 2rem;
        }}
        .fs-hero-text {{ flex: 1 1 auto; min-width: 0; }}
        .fs-hero-illustration {{
            flex: 0 0 220px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .fs-hero-illustration img {{ width: 100%; height: auto; max-width: 220px; display: block; }}
        @media (max-width: 900px) {{
            .fs-hero-flex {{ flex-direction: column; }}
            .fs-hero-illustration {{ flex-basis: auto; width: 170px; margin-top: 0.4rem; }}
        }}

        /* ---- "Bagaimana FitSense Bekerja?": alur horizontal 4 langkah ---- */
        .fs-flow {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 0.4rem;
            flex-wrap: wrap;
        }}
        .fs-flow-step {{
            flex: 1 1 0;
            min-width: 120px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 0.2rem 0.4rem;
        }}
        .fs-flow-icon {{
            width: 58px;
            height: 58px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 0.7rem;
            box-shadow: inset 0 0 0 1.5px rgba(169,130,31,0.22);
        }}
        .fs-flow-icon svg {{
            width: 26px;
            height: 26px;
            stroke: {INK};
            fill: none;
        }}
        .fs-flow-label {{
            font-weight: 700;
            font-size: 0.92rem;
            color: {TEXT} !important;
            margin-bottom: 0.25rem;
            font-family: 'Fraunces', Georgia, serif;
        }}
        .fs-flow-desc {{
            color: {MUTED} !important;
            font-size: 0.8rem;
            line-height: 1.45;
        }}
        .fs-flow-arrow {{
            flex: 0 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            padding-top: 22px;
            color: {BRASS};
            opacity: 0.65;
        }}
        .fs-flow-arrow svg {{ width: 20px; height: 20px; }}
        @media (max-width: 780px) {{
            .fs-flow {{ flex-direction: column; align-items: stretch; }}
            .fs-flow-step {{ width: 100%; }}
            .fs-flow-arrow {{ transform: rotate(90deg); padding: 0.2rem 0; }}
        }}

        /* ---- "Panduan Penggunaan": stepper 5 langkah ----
           Nomor urut sengaja dijadikan badge kecil yang menempel LANGSUNG
           di ikon tiap step (bukan grid nomor terpisah yang "diseberangkan"
           dengan grid ikon di baris lain). Dengan begini nomor & ikon selalu
           satu kesatuan yang sama, di jumlah kolom berapa pun — jadi tidak
           bisa lagi terpisah/berantakan saat grid berubah kolom di layar
           sempit (HP). */
        .fs-guide-flow {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 1.3rem 0.6rem;
        }}
        .fs-guide-step {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 0.6rem;
        }}
        .fs-guide-icon-wrap {{
            position: relative;
            width: 52px;
            height: 52px;
        }}
        .fs-guide-icon {{
            width: 52px;
            height: 52px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: inset 0 0 0 1.5px rgba(169,130,31,0.22);
        }}
        .fs-guide-icon svg {{
            width: 24px;
            height: 24px;
            stroke: {INK};
            fill: none;
        }}
        .fs-guide-num {{
            position: absolute;
            top: -6px;
            right: -6px;
            width: 21px;
            height: 21px;
            border-radius: 50%;
            background: linear-gradient(135deg, {BRASS_LIGHT} 0%, {BRASS} 100%);
            color: #FFFFFF !important;
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 700;
            font-size: 0.68rem;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 3px 8px rgba(169,130,31,0.4), 0 0 0 2px {SURFACE};
        }}
        .fs-guide-title {{
            font-weight: 600;
            font-size: 0.83rem;
            line-height: 1.35;
            color: {TEXT} !important;
        }}
        @media (max-width: 780px) {{
            .fs-guide-flow {{ grid-template-columns: repeat(3, 1fr); row-gap: 1.4rem; }}
        }}
        @media (max-width: 480px) {{
            .fs-guide-flow {{ grid-template-columns: repeat(2, 1fr); }}
        }}

        .fs-step {{
            display: flex;
            gap: 0.9rem;
            align-items: flex-start;
            padding: 0.9rem 0;
            border-bottom: 1px dashed {BORDER};
            transition: padding-left 0.15s ease;
        }}
        .fs-step:hover {{ padding-left: 4px; }}
        .fs-step:last-child {{ border-bottom: none; }}
        .fs-step-num {{
            flex-shrink: 0;
            width: 34px; height: 34px;
            border-radius: 50%;
            background: linear-gradient(135deg, {BRASS_SOFT}, #EFE1BC);
            color: {BRASS_DARK} !important;
            font-weight: 700;
            display: flex; align-items: center; justify-content: center;
            font-family: 'IBM Plex Mono', monospace;
            box-shadow: inset 0 0 0 1.5px rgba(169,130,31,0.35);
        }}
        .fs-step-title {{ font-weight: 600; margin-bottom: 2px; color: {TEXT} !important; }}
        .fs-step-desc {{ color: {MUTED} !important; font-size: 0.9rem; line-height: 1.5; }}

        /* ---- Intro pengukuran: grid kartu titik ukur (tanpa diagram siluet) ---- */
        .fs-legend-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.6rem;
        }}
        .fs-legend-item {{
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
            background: linear-gradient(180deg, {SURFACE} 0%, {BG} 100%);
            border: 1px solid {BORDER};
            border-radius: 11px;
            padding: 0.65rem 0.75rem;
            cursor: default;
            transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
        }}
        .fs-legend-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(169,130,31,0.14);
            border-color: {BRASS_LIGHT};
        }}
        .fs-legend-head {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
        }}
        .fs-legend-num {{
            flex-shrink: 0;
            width: 24px; height: 24px;
            border-radius: 50%;
            background: linear-gradient(135deg, {BRASS_SOFT}, #EFE1BC);
            color: {BRASS_DARK} !important;
            font-weight: 700;
            font-size: 0.78rem;
            display: flex; align-items: center; justify-content: center;
            font-family: 'IBM Plex Mono', monospace;
            box-shadow: inset 0 0 0 1.5px rgba(169,130,31,0.35);
        }}
        .fs-legend-title {{
            font-weight: 600;
            font-size: 0.83rem;
            line-height: 1.25;
            color: {TEXT} !important;
        }}
        .fs-legend-desc {{
            font-size: 0.78rem;
            line-height: 1.42;
            color: {MUTED} !important;
        }}
        @media (max-width: 900px) {{
            .fs-legend-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        @media (max-width: 560px) {{
            .fs-legend-grid {{ grid-template-columns: 1fr; }}
        }}

        /* ---- Badge status: pill dengan "lubang" gantungan tag di kiri,
           ala tag baju sungguhan (bukan pill polos lagi). ---- */
        .fs-badge {{
            position: relative;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 9px 22px 9px 36px;
            font-weight: 700;
            font-size: 0.98rem;
            font-family: 'Fraunces', Georgia, serif;
            color: white;
            border-radius: 999px;
            box-shadow: 0 6px 16px rgba(0,0,0,0.14);
        }}
        .fs-badge::before {{
            content: "";
            position: absolute;
            left: 15px; top: 50%; transform: translateY(-50%);
            width: 9px; height: 9px;
            border-radius: 50%;
            background: rgba(255,255,255,0.92);
            box-shadow: inset 0 0 0 1.5px rgba(0,0,0,0.18);
        }}
        .fs-badge-pas {{ background: linear-gradient(135deg, {PAS} 0%, #2C5C41 100%); }}
        .fs-badge-kecil {{ background: linear-gradient(135deg, {KECIL} 0%, #833327 100%); }}
        .fs-badge-besar {{ background: linear-gradient(135deg, {BESAR} 0%, #1F4F6C 100%); }}

        /* ---- Avatar wrap ---- */
        .fs-avatar-wrap {{
            display: flex;
            justify-content: center;
            padding: 0.5rem 0 0.3rem 0;
        }}
        .fs-avatar-photo {{
            position: relative;
            display: inline-block;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 20px rgba(27,42,74,0.14);
            background: {SURFACE};
        }}
        .fs-avatar-photo img {{
            display: block;
            width: 100%;
            height: auto;
        }}
        .fs-avatar-badge {{
            position: absolute;
            top: 8px;
            right: 8px;
            width: 26px;
            height: 26px;
            border-radius: 50%;
            background: {SURFACE};
            border: 2.5px solid var(--fs-badge-color, {BRASS});
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 0.85rem;
            line-height: 1;
            color: var(--fs-badge-color, {INK});
            box-shadow: 0 4px 10px rgba(0,0,0,0.18);
        }}

        /* ---- Perbandingan 3 panel: Terlalu Kecil / Pas / Terlalu Besar ---- */
        .fs-compare-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.9rem;
        }}
        .fs-compare-item {{
            background: {SURFACE};
            border: 2px solid {BORDER};
            border-radius: 16px;
            padding: 1rem 0.6rem 0.6rem 0.6rem;
            text-align: center;
            opacity: 0.6;
            transform: scale(0.96);
            transition: transform 0.2s ease, opacity 0.2s ease, box-shadow 0.2s ease;
        }}
        .fs-compare-item .fs-avatar-wrap {{
            filter: none;
            padding: 0.3rem 0 0;
        }}
        .fs-compare-item-active,
        .fs-compare-active {{
            opacity: 1;
            transform: scale(1);
            border-color: var(--fs-compare-color, {BRASS});
            background: linear-gradient(180deg, {SURFACE} 0%, {BG} 100%);
            box-shadow: 0 10px 24px rgba(27,42,74,0.12);
        }}
        .fs-compare-title {{
            font-family: 'Fraunces', Georgia, serif;
            font-weight: 700;
            font-size: 0.95rem;
            margin-bottom: 2px;
        }}
        .fs-compare-desc {{
            font-size: 0.74rem;
            color: {MUTED} !important;
            margin-bottom: 0.2rem;
        }}
        @media (max-width: 700px) {{
            .fs-compare-grid {{ grid-template-columns: 1fr; }}
            .fs-compare-item {{ display: flex; align-items: center; gap: 0.9rem; text-align: left; padding: 0.8rem; }}
            .fs-compare-item .fs-avatar-wrap {{ flex-shrink: 0; }}
        }}

        /* ---- Probabilitas: grid 3 kartu (ikon + angka besar + bar mini),
           bukan 3 baris bar lurus yang ditumpuk. ---- */
        .fs-proba-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.8rem;
        }}
        .fs-proba-card {{
            background: linear-gradient(180deg, {SURFACE} 0%, {BG} 100%);
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 1rem 0.9rem;
            text-align: center;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .fs-proba-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 22px rgba(169,130,31,0.14);
        }}
        .fs-proba-card-icon {{ font-size: 1.15rem; margin-bottom: 2px; }}
        .fs-proba-card-label {{ font-size: 0.8rem; font-weight: 600; color: {TEXT} !important; margin-bottom: 6px; }}
        .fs-proba-card-pct {{
            font-family: 'IBM Plex Mono', 'Courier New', monospace !important;
            font-weight: 700;
            font-size: 1.3rem;
            color: var(--pc-color, {INK}) !important;
            margin-bottom: 2px;
        }}
        /* Gauge setengah lingkaran (bukan bar lurus lagi) */
        .fs-proba-card-gauge {{
            width: 78px; height: 40px;
            margin: 2px auto 0;
            position: relative;
            overflow: hidden;
        }}
        .fs-proba-card-gauge-fill {{
            position: absolute; top: 0; left: 0;
            width: 78px; height: 78px;
            border-radius: 50%;
            background: conic-gradient(from -90deg, var(--pc-color, {BRASS}) calc(var(--pct, 0) * 0.5%), {BORDER} 0);
        }}
        .fs-proba-card-gauge-fill::after {{
            content: "";
            position: absolute;
            top: 9px; left: 9px;
            width: 60px; height: 60px;
            border-radius: 50%;
            background: {SURFACE};
        }}
        @media (max-width: 640px) {{
            .fs-proba-grid {{ grid-template-columns: 1fr; }}
        }}

        .fs-info-pill {{
            background: linear-gradient(180deg, {SURFACE} 0%, {BG} 100%);
            border: 1px solid {BORDER};
            border-radius: 13px;
            padding: 12px 14px;
            text-align: center;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .fs-info-pill:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 18px rgba(169,130,31,0.14);
        }}
        .fs-info-pill-label {{ font-size: 0.75rem; color: {MUTED} !important; margin-bottom: 3px; }}
        .fs-info-pill-value {{ font-weight: 700; color: {INK} !important; font-size: 0.98rem; }}

        /* Varian pill dengan medali ikon di kiri (dipakai utk Kategori Usia/Tinggi) */
        .fs-info-pill-icon {{
            display: flex;
            align-items: center;
            gap: 0.7rem;
            text-align: left;
        }}
        .fs-info-pill-icon .fs-info-pill-badge {{
            flex-shrink: 0;
            width: 34px; height: 34px;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            box-shadow: inset 0 0 0 1.5px rgba(169,130,31,0.28);
        }}
        .fs-info-pill-icon .fs-info-pill-badge svg {{ width: 17px; height: 17px; stroke: {INK}; fill: none; }}

        .fs-explain-box {{
            background: {BG};
            border-left: 3px solid {BRASS};
            border-radius: 10px;
            padding: 0.95rem 1.15rem;
            font-size: 0.93rem;
            color: {TEXT} !important;
            line-height: 1.55;
        }}
        .fs-explain-box b {{ color: {TEXT} !important; }}

        /* ---- Sub-judul kecil di dalam kartu: "eyebrow caption" ringkas & rapi,
           dipakai di atas panel probabilitas / kartu catatan, alih-alih bold
           markdown polos bawaan Streamlit yang beda font & ukurannya. ---- */
        .fs-subheading {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-family: 'IBM Plex Sans', sans-serif;
            font-weight: 700;
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: {BRASS_DARK} !important;
            margin: 0 0 0.65rem 0;
        }}

        /* ---- Cincin keyakinan model: donut ala kancing kuningan, dengan
           angka besar mono di tengah supaya jadi titik fokus visual. ---- */
        .fs-confidence-wrap {{
            display: flex;
            align-items: center;
            gap: 1.3rem;
            padding: 0.3rem 0.2rem;
        }}
        .fs-confidence-ring {{
            flex-shrink: 0;
            position: relative;
            width: 108px; height: 108px;
            border-radius: 50%;
            background: conic-gradient(var(--ring-color, {BRASS}) calc(var(--pct, 0) * 1%), {BORDER} 0);
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 8px 20px rgba(27,42,74,0.12);
        }}
        .fs-confidence-ring::after {{
            content: "";
            position: absolute;
            top: -5px; left: 50%; transform: translateX(-50%);
            width: 13px; height: 13px;
            border-radius: 50%;
            background: {BG};
            border: 1.5px dashed {BORDER};
        }}
        .fs-confidence-ring-inner {{
            width: 84px; height: 84px;
            border-radius: 50%;
            background: {SURFACE};
            box-shadow: inset 0 0 0 1px {BORDER};
            display: flex; flex-direction: column; align-items: center; justify-content: center;
        }}
        .fs-confidence-value {{
            font-family: 'IBM Plex Mono', 'Courier New', monospace;
            font-weight: 700;
            font-size: 1.28rem;
            color: {INK} !important;
            line-height: 1;
        }}
        .fs-confidence-caption {{
            font-size: 0.9rem;
            color: {MUTED} !important;
            line-height: 1.4;
        }}
        .fs-confidence-caption b {{ color: {TEXT} !important; }}
        @media (max-width: 560px) {{
            .fs-confidence-wrap {{ flex-direction: column; text-align: center; }}
        }}

        /* ---- Panel cincin hero (Informasi Model > Performa Model): membungkus
           cincin akurasi dalam kartu tersendiri supaya seimbang dengan grid
           kartu metrik di sebelahnya, bukan cincin telanjang mengambang. ---- */
        .fs-hero-ring-panel {{
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 0.9rem;
            background: linear-gradient(180deg, {SURFACE} 0%, {BG} 100%);
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 1.6rem 1.3rem;
            text-align: center;
        }}
        .fs-confidence-ring-lg {{ width: 148px; height: 148px; }}
        .fs-confidence-ring-inner-lg {{ width: 122px; height: 122px; }}
        .fs-confidence-value-lg {{ font-size: 1.7rem; }}
        .fs-confidence-sublabel {{
            font-family: 'IBM Plex Sans', sans-serif;
            font-weight: 700;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: {BRASS_DARK} !important;
            margin-top: 2px;
        }}
        .fs-hero-ring-panel .fs-confidence-caption {{ max-width: 220px; font-size: 0.86rem; }}

        /* ---- Grid kartu metrik (Precision/Recall/F1) — tiga kartu seragam
           dengan mini progress bar, menggantikan pil bertumpuk vertikal. ---- */
        .fs-metric-grid {{
            height: 100%;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.8rem;
        }}
        .fs-metric-card {{
            display: flex;
            flex-direction: column;
            gap: 0.65rem;
            background: linear-gradient(180deg, {SURFACE} 0%, {BG} 100%);
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 1rem 1.05rem;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .fs-metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 22px rgba(169,130,31,0.14);
        }}
        .fs-metric-card-head {{ display: flex; align-items: center; gap: 0.55rem; }}
        .fs-metric-card-badge {{
            flex-shrink: 0;
            width: 32px; height: 32px;
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            box-shadow: inset 0 0 0 1.5px rgba(169,130,31,0.28);
        }}
        .fs-metric-card-label {{ font-size: 0.72rem; color: {MUTED} !important; line-height: 1.25; }}
        .fs-metric-card-value {{
            font-family: 'IBM Plex Mono', 'Courier New', monospace;
            font-weight: 700;
            font-size: 1.28rem;
            color: {INK} !important;
            line-height: 1;
        }}
        .fs-metric-card-track {{ height: 6px; border-radius: 999px; background: {BORDER}; overflow: hidden; }}
        .fs-metric-card-fill {{ height: 100%; border-radius: 999px; }}
        @media (max-width: 760px) {{
            .fs-metric-grid {{ grid-template-columns: 1fr; }}
        }}

        /* Varian grid metrik 4 kolom (Accuracy/Precision/Recall/F1 seragam) */
        .fs-metric-grid-4 {{
            grid-template-columns: repeat(4, 1fr);
        }}
        @media (max-width: 980px) {{
            .fs-metric-grid-4 {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        @media (max-width: 560px) {{
            .fs-metric-grid-4 {{ grid-template-columns: 1fr; }}
        }}

        /* ---- Garis pemisah vertikal antar kartu berdampingan (mis. Proses
           Pemodelan vs Feature Importance) — jahitan putus-putus tipis yang
           merentang penuh mengikuti tinggi kartu di sebelahnya. ---- */
        .fs-vdivider {{
            width: 1px;
            height: 100%;
            min-height: 100%;
            background-image: repeating-linear-gradient(180deg, {BORDER} 0 6px, transparent 6px 12px);
            margin: 0 auto;
        }}
        div[data-testid="stHorizontalBlock"] {{ align-items: stretch; }}
        @media (max-width: 900px) {{
            .fs-vdivider {{ display: none; }}
        }}

        /* ---- Grid kartu Rincian per Kelas — kartu bertepi warna status,
           menggantikan daftar bar polos yang ditumpuk. ---- */
        .fs-class-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.9rem;
        }}
        .fs-class-card {{
            background: linear-gradient(180deg, {SURFACE} 0%, {BG} 100%);
            border: 1px solid {BORDER};
            border-left: 4px solid var(--class-color, {BRASS});
            border-radius: 14px;
            padding: 1rem 1.1rem;
            display: flex;
            flex-direction: column;
            gap: 0.7rem;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .fs-class-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 22px rgba(27,42,74,0.1);
        }}
        .fs-class-card-head {{ display: flex; align-items: baseline; justify-content: space-between; gap: 0.5rem; }}
        .fs-class-card-name {{
            display: flex;
            align-items: center;
            font-family: 'Fraunces', Georgia, serif;
            font-weight: 700;
            font-size: 0.98rem;
            color: {TEXT} !important;
        }}
        .fs-class-card-f1 {{
            font-family: 'IBM Plex Mono', 'Courier New', monospace;
            font-weight: 700;
            font-size: 1.15rem;
            color: var(--class-color, {INK}) !important;
            white-space: nowrap;
        }}
        .fs-class-card-track {{ height: 8px; border-radius: 999px; background: {BORDER}; overflow: hidden; }}
        .fs-class-card-fill {{
            height: 100%;
            border-radius: 999px;
            background: var(--class-color, {BRASS});
            transition: width 0.6s ease;
        }}
        .fs-class-card-meta {{
            display: flex;
            justify-content: space-between;
            gap: 0.4rem;
            font-size: 0.76rem;
            color: {MUTED} !important;
            font-family: 'IBM Plex Mono', 'Courier New', monospace;
        }}
        .fs-class-card-meta b {{ color: {TEXT} !important; }}
        @media (max-width: 900px) {{
            .fs-class-grid {{ grid-template-columns: 1fr; }}
        }}

        /* ---- Strip statistik cepat di atas Confusion Matrix (benar/salah/total) ---- */
        .fs-cm-stats {{ display: flex; gap: 0.8rem; margin-bottom: 1.1rem; flex-wrap: wrap; }}
        .fs-cm-stat {{
            flex: 1 1 170px;
            display: flex;
            align-items: center;
            gap: 0.7rem;
            background: linear-gradient(180deg, {SURFACE} 0%, {BG} 100%);
            border: 1px solid {BORDER};
            border-radius: 13px;
            padding: 0.8rem 1rem;
        }}
        .fs-cm-stat-badge {{
            flex-shrink: 0;
            width: 36px; height: 36px;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            box-shadow: inset 0 0 0 1.5px rgba(169,130,31,0.28);
        }}
        .fs-cm-stat-badge svg {{ width: 17px; height: 17px; fill: none; }}
        .fs-cm-stat-label {{ font-size: 0.72rem; color: {MUTED} !important; text-transform: uppercase; letter-spacing: 0.03em; }}
        .fs-cm-stat-value {{
            font-family: 'IBM Plex Mono', 'Courier New', monospace;
            font-weight: 700;
            font-size: 1.18rem;
            color: {INK} !important;
        }}

        /* ---- Kartu catatan (Penjelasan Singkat / Rekomendasi Ukuran) dengan
           medali ikon, versi lebih hidup dari .fs-explain-box polos. ---- */
        .fs-note-card {{
            display: flex;
            gap: 0.9rem;
            align-items: flex-start;
            background: {BG};
            border: 1px solid {BORDER};
            border-left: 4px solid var(--note-color, {BRASS});
            border-radius: 12px;
            padding: 1rem 1.15rem;
        }}
        .fs-note-icon {{
            flex-shrink: 0;
            width: 32px; height: 32px;
            border-radius: 50%;
            background: {SURFACE};
            display: flex; align-items: center; justify-content: center;
            font-size: 1rem;
            box-shadow: inset 0 0 0 1.5px rgba(169,130,31,0.28);
        }}
        .fs-note-text {{
            font-size: 0.93rem;
            color: {TEXT} !important;
            line-height: 1.55;
        }}
        .fs-note-text b {{ color: {TEXT} !important; }}

        /* ---- SHAP: faktor pendorong prediksi, ditata sebagai daftar bar
           lurus yang ditumpuk (satu baris per fitur), bar menyimpang dari
           titik tengah track -- kanan = mendorong ke arah status, kiri =
           menahan/berlawanan. Diurutkan dari pengaruh terbesar ke terkecil. ---- */
        .fs-shap-rows {{
            display: flex;
            flex-direction: column;
            gap: 1.05rem;
        }}
        .fs-shap-row-top {{
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 0.6rem;
            margin-bottom: 0.4rem;
        }}
        .fs-shap-row-label {{
            font-weight: 600;
            font-size: 0.88rem;
            color: {TEXT} !important;
        }}
        .fs-shap-row-value {{
            font-family: 'IBM Plex Mono', 'Courier New', monospace !important;
            font-size: 0.8rem;
            color: {MUTED} !important;
            white-space: nowrap;
        }}
        .fs-shap-track {{
            position: relative;
            background: {BG};
            border: 1px solid {BORDER};
            border-radius: 999px;
            height: 9px;
            overflow: hidden;
        }}
        .fs-shap-fill {{
            position: absolute;
            top: 0;
            height: 100%;
            border-radius: 999px;
            transition: width 0.6s ease, left 0.6s ease;
        }}

        .fs-shap-legend {{
            display: flex; gap: 10px; flex-wrap: wrap;
            font-size: 0.78rem; color: {MUTED} !important; margin: 0 0 0.9rem 0;
        }}
        .fs-shap-legend span {{
            display: inline-flex; align-items: center; gap: 6px;
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 999px;
            padding: 4px 12px 4px 9px;
        }}
        .fs-shap-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; }}

        /* =====================================================================
           "KARTU KAIN UKUR": profil (usia/tinggi) + cincin keyakinan disatukan
           dalam satu kartu, dipisah garis jahitan putus-putus vertikal --
           kesannya seperti tiket/label butik yang dilipat dua, bukan 3 baris
           kotak terpisah yang ditumpuk ke bawah.
           ===================================================================== */
        .fs-fit-profile {{
            display: grid;
            grid-template-columns: minmax(0,1fr) auto minmax(0,1.15fr);
            align-items: center;
            gap: 1.4rem;
            background: linear-gradient(135deg, {SURFACE} 0%, {BG} 100%);
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 1.15rem 1.5rem;
        }}
        .fs-fit-profile-tags {{
            display: flex;
            flex-direction: column;
            gap: 0.7rem;
        }}
        .fs-fit-tag {{
            display: flex;
            align-items: center;
            gap: 0.7rem;
        }}
        .fs-fit-tag-icon {{
            flex-shrink: 0;
            width: 36px; height: 36px;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            box-shadow: inset 0 0 0 1.5px rgba(169,130,31,0.28);
        }}
        .fs-fit-tag-icon svg {{ width: 17px; height: 17px; stroke: {INK}; fill: none; }}
        .fs-fit-tag-label {{
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: {MUTED} !important;
            margin-bottom: 1px;
        }}
        .fs-fit-tag-value {{
            font-family: 'Fraunces', Georgia, serif;
            font-weight: 700;
            font-size: 1.02rem;
            color: {TEXT} !important;
            line-height: 1.2;
        }}
        .fs-fit-profile-divider {{
            width: 0;
            align-self: stretch;
            border-left: 1.5px dashed {BORDER};
            position: relative;
        }}
        .fs-fit-profile-divider::before,
        .fs-fit-profile-divider::after {{
            content: "";
            position: absolute;
            left: 50%; transform: translateX(-50%);
            width: 9px; height: 9px;
            border-radius: 50%;
            background: {BG};
            border: 1.5px solid {BORDER};
        }}
        .fs-fit-profile-divider::before {{ top: -4px; }}
        .fs-fit-profile-divider::after {{ bottom: -4px; }}
        .fs-fit-profile-confidence {{
            display: flex;
            align-items: center;
            gap: 1.1rem;
        }}
        @media (max-width: 760px) {{
            .fs-fit-profile {{ grid-template-columns: 1fr; }}
            .fs-fit-profile-divider {{
                width: auto; height: 0; align-self: auto;
                border-left: none; border-top: 1.5px dashed {BORDER};
                margin: 0.3rem 0;
            }}
            .fs-fit-profile-divider::before,
            .fs-fit-profile-divider::after {{ top: 50%; transform: translateY(-50%); left: auto; }}
            .fs-fit-profile-divider::before {{ left: -4px; }}
            .fs-fit-profile-divider::after {{ left: auto; right: -4px; }}
        }}

        /* =====================================================================
           Probabilitas sebagai bar horizontal yang ditumpuk ke bawah --
           label di kiri & persentase di kanan pada baris yang sama, lalu
           track penuh selebar kartu di bawahnya. Sengaja disamakan dengan
           gaya baris pada bagian "Faktor Paling Berpengaruh" supaya kedua
           bagian terasa satu keluarga visual.
           ===================================================================== */
        .fs-proba-bar-list {{
            display: flex;
            flex-direction: column;
            gap: 1.15rem;
        }}
        .fs-proba-bar-head {{
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            margin-bottom: 0.4rem;
        }}
        .fs-proba-bar-label {{
            font-weight: 700;
            font-size: 0.92rem;
            color: {TEXT} !important;
        }}
        .fs-proba-bar-flag {{
            display: inline-block;
            font-size: 0.62rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            color: white !important;
            padding: 1px 8px;
            border-radius: 999px;
            margin-left: 4px;
            position: relative;
            top: -1px;
        }}
        .fs-proba-bar-pct {{
            font-family: 'IBM Plex Mono', 'Courier New', monospace !important;
            font-size: 0.84rem;
            color: {MUTED} !important;
        }}
        .fs-proba-bar-track {{
            position: relative;
            background: {BG};
            border: 1px solid {BORDER};
            border-radius: 999px;
            height: 12px;
            overflow: hidden;
        }}
        .fs-proba-bar-fill {{
            height: 100%;
            border-radius: 999px;
            transition: width 0.6s ease;
        }}

        /* =====================================================================
           "Kartu dua sisi" -- Penjelasan Singkat & Rekomendasi Ukuran disatukan
           berdampingan, dipisah garis jahitan vertikal dengan kancing kuningan
           kecil di tengah, alih-alih dua fs-note-card yang ditumpuk ke bawah.
           ===================================================================== */
        .fs-insight-duo {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0;
            background: {BG};
            border: 1px solid {BORDER};
            border-radius: 14px;
            overflow: hidden;
            position: relative;
        }}
        .fs-insight-half {{
            padding: 1.1rem 1.3rem;
            display: flex;
            flex-direction: column;
            gap: 0.55rem;
        }}
        .fs-insight-half + .fs-insight-half {{
            border-left: 1.5px dashed {BORDER};
        }}
        .fs-insight-duo::after {{
            content: "";
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            width: 20px; height: 20px;
            border-radius: 50%;
            background: radial-gradient(circle at 35% 30%, {BRASS_LIGHT}, {BRASS_DARK});
            box-shadow: 0 2px 6px rgba(0,0,0,0.25), inset 0 0 0 2px rgba(255,255,255,0.35);
            display: none;
        }}
        @media (min-width: 761px) {{ .fs-insight-duo::after {{ display: block; }} }}
        .fs-insight-head {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
        }}
        .fs-insight-icon {{
            flex-shrink: 0;
            width: 30px; height: 30px;
            border-radius: 50%;
            background: {SURFACE};
            display: flex; align-items: center; justify-content: center;
            font-size: 0.95rem;
            box-shadow: inset 0 0 0 1.5px rgba(169,130,31,0.28);
        }}
        .fs-insight-title {{
            font-family: 'IBM Plex Sans', sans-serif;
            font-weight: 700;
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--insight-color, {BRASS_DARK}) !important;
        }}
        .fs-insight-text {{
            font-size: 0.9rem;
            color: {TEXT} !important;
            line-height: 1.55;
        }}
        .fs-insight-text b {{ color: {TEXT} !important; }}
        @media (max-width: 760px) {{
            .fs-insight-duo {{ grid-template-columns: 1fr; }}
            .fs-insight-half + .fs-insight-half {{
                border-left: none;
                border-top: 1.5px dashed {BORDER};
            }}
        }}

        /* ---- Informasi Model: kartu ringkas Algoritma/Dataset/Target ---- */
        .fs-model-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
        }}
        .fs-model-item {{
            display: flex;
            flex-direction: column;
            gap: 0.7rem;
            align-items: flex-start;
            background: linear-gradient(180deg, {SURFACE} 0%, {BG} 100%);
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 1.05rem 1.1rem;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .fs-model-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 22px rgba(169,130,31,0.14);
        }}
        .fs-model-item > div:last-child {{ width: 100%; }}
        .fs-model-icon {{
            flex-shrink: 0;
            width: 42px; height: 42px;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            box-shadow: inset 0 0 0 1.5px rgba(169,130,31,0.28);
        }}
        .fs-model-icon svg {{ width: 21px; height: 21px; stroke: {INK}; fill: none; }}
        .fs-model-label {{
            font-size: 0.74rem;
            color: {MUTED} !important;
            margin-bottom: 1px;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }}
        .fs-model-value {{
            font-family: 'Fraunces', Georgia, serif;
            font-weight: 700;
            font-size: 1.05rem;
            color: {TEXT} !important;
            line-height: 1.25;
            min-height: 2.65rem;
            display: flex;
            align-items: flex-start;
        }}
        .fs-model-desc {{ color: {MUTED} !important; font-size: 0.8rem; line-height: 1.4; margin-top: 0.5em; }}
        @media (max-width: 900px) {{
            .fs-model-grid {{ grid-template-columns: 1fr; }}
        }}

        /* ---- Kotak highlight (kesimpulan) di dasar kartu ---- */
        .fs-highlight-box {{
            display: flex;
            align-items: center;
            gap: 0.9rem;
            background: linear-gradient(135deg, {BRASS_SOFT} 0%, {INK_SOFT} 100%);
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 1rem 1.3rem;
            margin-top: 0.3rem;
        }}
        .fs-highlight-icon {{
            flex-shrink: 0;
            width: 38px; height: 38px;
            border-radius: 50%;
            background: linear-gradient(135deg, {INK} 0%, {INK_DARK} 100%);
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 6px 14px rgba(14,24,48,0.28);
        }}
        .fs-highlight-icon svg {{ width: 18px; height: 18px; stroke: {BRASS_LIGHT}; fill: none; }}
        .fs-highlight-box p {{ margin: 0; font-size: 0.92rem; color: {TEXT} !important; line-height: 1.5; }}

        .stButton>button,
        [data-testid^="stBaseButton-"] {{
            border-radius: 10px;
            font-weight: 600;
            font-family: 'IBM Plex Sans', sans-serif;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .stButton>button[kind="primary"],
        [data-testid="stBaseButton-primary"] {{
            background: linear-gradient(135deg, {INK} 0%, {INK_DARK} 100%) !important;
            border-color: {INK_DARK} !important;
            color: {BRASS_LIGHT} !important;
            box-shadow: 0 8px 20px rgba(14,24,48,0.28);
        }}
        .stButton>button[kind="primary"] *,
        [data-testid="stBaseButton-primary"] * {{
            color: {BRASS_LIGHT} !important;
            fill: {BRASS_LIGHT} !important;
        }}
        .stButton>button[kind="primary"]:hover,
        [data-testid="stBaseButton-primary"]:hover {{
            transform: translateY(-1px);
            box-shadow: 0 10px 24px rgba(14,24,48,0.36);
        }}
        .stButton>button:not([kind="primary"]):hover,
        [data-testid^="stBaseButton-"]:not([data-testid="stBaseButton-primary"]):hover {{
            transform: translateY(-1px);
        }}

        /* Tombol submit form ("Prediksi Ukuran") — dipastikan lagi secara
           eksplisit di sini (selain aturan primary umum di atas) supaya
           tulisan & ikonnya tetap jelas terbaca di atas latar gelap,
           terlepas dari versi Streamlit yang dipakai. */
        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stFormSubmitButton"] [data-testid^="stBaseButton-"] {{
            background: linear-gradient(135deg, {INK} 0%, {INK_DARK} 100%) !important;
            border-color: {INK_DARK} !important;
            color: {BRASS_LIGHT} !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
        }}
        div[data-testid="stFormSubmitButton"] button *,
        div[data-testid="stFormSubmitButton"] [data-testid^="stBaseButton-"] * {{
            color: {BRASS_LIGHT} !important;
            fill: {BRASS_LIGHT} !important;
            font-weight: 700 !important;
        }}
        div[data-testid="stFormSubmitButton"] button:hover,
        div[data-testid="stFormSubmitButton"] [data-testid^="stBaseButton-"]:hover {{
            transform: translateY(-1px);
            box-shadow: 0 10px 24px rgba(14,24,48,0.36);
        }}

        div[data-testid="stForm"] {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 18px;
            padding: 1.7rem 1.9rem 0.7rem 1.9rem;
            box-shadow: 0 10px 28px rgba(27,42,74,0.06);
        }}

        div.block-container {{
            padding-top: 2.1rem;
            max-width: 1180px;
        }}

        /* =====================================================================
           Header bawaan Streamlit: sembunyikan menu bawaan (MainMenu),
           toolbar "Deploy", garis dekorasi warna-warni, dan status widget —
           TAPI header itu sendiri TIDAK di-`display:none` total, karena
           tombol untuk membuka kembali sidebar yang ter-collapse (selalu
           ter-collapse otomatis di layar sempit / HP) dirender di DALAM
           elemen header ini. Kalau headernya di-`display:none`, tombol itu
           ikut hilang dan sidebar jadi tidak bisa dibuka lagi di HP —
           itulah penyebab sidebar "hilang" saat dibuka lewat HP.
           Sebagai gantinya header dibuat transparan & setipis mungkin,
           supaya tetap terasa "tanpa bar kosong" di desktop, tapi tombol
           toggle-nya tetap terlihat & bisa dipakai di semua ukuran layar.
           ===================================================================== */
        header[data-testid="stHeader"] {{
            background: transparent !important;
            box-shadow: none !important;
            height: 2.6rem !important;
            min-height: 2.6rem !important;
        }}
        /* PENTING: JANGAN sembunyikan div[data-testid="stToolbar"] secara
           keseluruhan — tombol "buka sidebar" (stExpandSidebarButton) yang
           muncul saat sidebar ter-collapse ternyata dirender sebagai anak
           dari container stToolbar yang sama (terverifikasi lewat inspeksi
           DOM). Kalau seluruh stToolbar disembunyikan, tombol itu ikut
           kehilangan ukuran (0x0) dan tidak bisa diklik sama sekali —
           itulah akar masalah "sidebar tidak bisa dibuka di HP" sebelumnya.
           Jadi di sini hanya bagian menu titik-tiga & area tombol Deploy
           saja yang disembunyikan, bukan kontainernya. */
        div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"],
        #MainMenu,
        [data-testid="stMainMenu"],
        [data-testid="stToolbarActions"] {{
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }}
        div[data-testid="stAppViewContainer"] > .main {{
            padding-top: 0.4rem !important;
        }}

        @media (max-width: 640px) {{
            .fs-hero {{ padding: 1.9rem 1.5rem; }}
            .fs-hero-title {{ font-size: 1.55rem; }}
            .fs-card {{ padding: 1.3rem 1.3rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
