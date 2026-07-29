"""
ui_components.py
=================
Komponen tampilan (CSS, ikon SVG kustom, card helper) untuk FitSense.
Semua ikon dibuat sebagai SVG monoline (bukan emoji) agar tampil profesional,
konsisten dengan referensi desain (rounded, soft pink, clean).
"""

import streamlit as st

PRIMARY = "#D6336C"
PRIMARY_DARK = "#B02154"
PRIMARY_LIGHT = "#FDEEF3"
PRIMARY_SOFT = "#FCE4EC"
INK = "#3A2233"
INK_SOFT = "#7A6672"
BG = "#FDF6F8"
SUCCESS = "#1E9E63"
SUCCESS_BG = "#E7F8EF"
WARNING = "#D97706"
WARNING_BG = "#FEF3E2"
DANGER = "#DC3452"
DANGER_BG = "#FDECEF"


def icon(name: str, size: int = 20, color: str = "currentColor", stroke_width: float = 1.8) -> str:
    """Mengembalikan markup SVG monoline untuk nama ikon yang diminta."""
    common = f'width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" ' \
             f'stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"'

    paths = {
        "home": '<path d="M4 11.5 12 4l8 7.5"/><path d="M6 10v9a1 1 0 0 0 1 1h3v-6h4v6h3a1 1 0 0 0 1-1v-9"/>',
        "ruler": '<rect x="3" y="8" width="18" height="8" rx="1.5"/><path d="M7 8v3M11 8v3M15 8v3"/>',
        "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
        "user": '<circle cx="12" cy="8" r="3.4"/><path d="M5 20c1-3.5 4-5.5 7-5.5s6 2 7 5.5"/>',
        "users": '<circle cx="9" cy="8" r="3"/><path d="M3 20c.7-3 3-5 6-5s5.3 2 6 5"/><circle cx="17" cy="9" r="2.4"/><path d="M15.5 15.2c2.2.2 3.9 1.9 4.5 4.3"/>',
        "check-circle": '<circle cx="12" cy="12" r="9"/><path d="m8.2 12.3 2.6 2.6 5-5.4"/>',
        "alert": '<path d="M12 3.5 21.5 20h-19z"/><path d="M12 9.5v4.2"/><circle cx="12" cy="16.6" r="0.6" fill="' + color + '"/>',
        "lightbulb": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.5.4.9 1 .9 1.7v.5h5.4v-.5c0-.7.4-1.3.9-1.7A6 6 0 0 0 12 3Z"/>',
        "arrow-right": '<path d="M4 12h16M14 6l6 6-6 6"/>',
        "arrow-left": '<path d="M20 12H4M10 6l-6 6 6 6"/>',
        "layers": '<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 13 9 5 9-5"/>',
        "target": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5" fill="' + color + '"/>',
        "cpu": '<rect x="6" y="6" width="12" height="12" rx="1.5"/><rect x="9.5" y="9.5" width="5" height="5" rx="0.5"/><path d="M9 3v3M15 3v3M9 18v3M15 18v3M3 9h3M3 15h3M18 9h3M18 15h3"/>',
        "database": '<ellipse cx="12" cy="5.5" rx="7" ry="2.5"/><path d="M5 5.5V17c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V5.5"/><path d="M5 11.3c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5"/>',
        "calendar": '<rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M8 3v4M16 3v4M3.5 10h17"/>',
        "shirt": '<path d="M8 4 5 6.5 3 9l3 2v9.5h12V11l3-2-2-2.5L16 4c-1 1.6-2.4 2.5-4 2.5S9 5.6 8 4Z"/>',
        "sparkles": '<path d="M12 3v4M12 17v4M4 12h4M16 12h4"/><path d="m6 6 2 2M16 16l2 2M18 6l-2 2M8 16l-2 2"/>',
        "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.01"/>',
        "list": '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1.2" fill="' + color + '"/><circle cx="4.5" cy="12" r="1.2" fill="' + color + '"/><circle cx="4.5" cy="18" r="1.2" fill="' + color + '"/>',
        "settings": '<circle cx="12" cy="12" r="3"/><path d="M19.4 13.5c.1-.5.1-1 0-1.5l1.8-1.4-2-3.4-2.1.7c-.4-.3-.8-.6-1.3-.8l-.3-2.2h-4l-.3 2.2c-.5.2-.9.5-1.3.8l-2.1-.7-2 3.4L4.6 12c-.1.5-.1 1 0 1.5l-1.8 1.4 2 3.4 2.1-.7c.4.3.8.6 1.3.8l.3 2.2h4l.3-2.2c.5-.2.9-.5 1.3-.8l2.1.7 2-3.4Z"/>',
        "book": '<path d="M4 5.5C4 4.7 4.7 4 5.5 4H12v16H5.5A1.5 1.5 0 0 1 4 18.5Z"/><path d="M20 5.5c0-.8-.7-1.5-1.5-1.5H12v16h6.5a1.5 1.5 0 0 0 1.5-1.5Z"/>',
        "trend": '<path d="m3 17 6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
        "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
        "hanger": '<path d="M12 3.2a1.6 1.6 0 1 1 1.7 1.6c-.1 0-.2 0-.2.1 0 .1 0 .3.2.4L21 9.5c.9.5.6 1.8-.4 1.8H3.4c-1 0-1.3-1.3-.4-1.8l7.3-4.2c.2-.1.2-.3.2-.4 0-.1-.1-.1-.2-.1"/><path d="M3 15.5h18"/>',
        "scale": '<path d="M12 3v18M7 7l-3.5 7a3.5 3.5 0 0 0 7 0Zm10 0-3.5 7a3.5 3.5 0 0 0 7 0Z"/><path d="M5 21h14M4 6.5h16"/>',
        "check": '<path d="m5 12.5 4.5 4.5L19 7"/>',
        "x": '<path d="M6 6l12 12M18 6 6 18"/>',
        "map": '<path d="M9 4 3.5 6v14L9 18l6 2 5.5-2V4L15 6 9 4Z"/><path d="M9 4v14M15 6v14"/>',
        "percent": '<circle cx="7" cy="7" r="2.2"/><circle cx="17" cy="17" r="2.2"/><path d="M18 6 6 18"/>',
    }
    body = paths.get(name, paths["info"])
    return f'<svg {common}>{body}</svg>'


def inject_base_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"]  {{
        font-family: 'Inter', sans-serif;
    }}
    h1, h2, h3, h4, .fs-heading {{
        font-family: 'Poppins', sans-serif !important;
        color: {INK};
    }}

    .stApp {{
        background: linear-gradient(180deg, {BG} 0%, #FFFFFF 340px);
    }}

    #MainMenu, footer, header {{visibility: hidden;}}
    .block-container {{ padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1200px;}}

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {{
        background: #FFFFFF;
        border-right: 1px solid #F3D9E2;
    }}
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 1.6rem;
    }}

    .fs-logo-wrap {{
        display:flex; align-items:center; gap:12px;
        padding: 4px 4px 22px 4px;
        border-bottom: 1px solid #F5E1E8;
        margin-bottom: 18px;
    }}
    .fs-logo-icon {{
        width:44px; height:44px; border-radius:14px;
        background: linear-gradient(135deg,{PRIMARY} 0%, #F06292 100%);
        display:flex; align-items:center; justify-content:center;
        color:white; flex-shrink:0;
        box-shadow: 0 6px 14px rgba(214,51,108,0.35);
    }}
    .fs-logo-title {{
        font-family:'Poppins',sans-serif; font-weight:700; font-size:1.15rem; color:{INK}; line-height:1.1;
    }}
    .fs-logo-sub {{
        font-size:0.72rem; color:{INK_SOFT}; margin-top:2px;
    }}

    .fs-nav-item {{
        display:flex; align-items:center; gap:12px;
        padding:10px 14px; border-radius:12px; margin-bottom:6px;
        font-weight:500; font-size:0.92rem; color:{INK_SOFT};
        cursor:pointer; transition: all .15s ease;
    }}
    .fs-nav-item.active {{
        background: linear-gradient(135deg,{PRIMARY} 0%, #E85D8C 100%);
        color:#fff; box-shadow: 0 6px 14px rgba(214,51,108,0.28);
        font-weight:600;
    }}
    .fs-nav-item svg {{ flex-shrink:0; }}

    section[data-testid="stSidebar"] .stButton button {{
        width:100%; text-align:left; border:none; background:transparent;
        padding:10px 14px; border-radius:12px; font-weight:500; font-size:0.92rem;
        color:{INK_SOFT}; box-shadow:none; transition:.15s;
    }}
    section[data-testid="stSidebar"] .stButton button:hover {{
        background:{PRIMARY_LIGHT}; color:{PRIMARY_DARK};
    }}
    section[data-testid="stSidebar"] .stButton button p {{ text-align:left; }}

    .fs-sidebar-footer {{
        position:fixed; bottom:18px; font-size:0.72rem; color:#B7A3AC;
        padding-left:4px;
    }}

    /* ---------- Cards ---------- */
    .fs-card {{
        background:#fff; border-radius:18px; padding:24px 26px;
        box-shadow: 0 4px 22px rgba(214,51,108,0.07);
        border: 1px solid #FBEAF0;
        margin-bottom: 20px;
    }}
    .fs-card-title {{
        display:flex; align-items:center; gap:10px;
        font-family:'Poppins',sans-serif; font-weight:600; font-size:1.02rem;
        color:{INK}; margin-bottom:14px;
    }}
    .fs-card-title .fs-icon-badge {{
        width:32px; height:32px; border-radius:10px; background:{PRIMARY_SOFT};
        display:flex; align-items:center; justify-content:center; color:{PRIMARY_DARK};
        flex-shrink:0;
    }}

    .fs-pill {{
        display:inline-flex; align-items:center; gap:8px;
        background:{PRIMARY_SOFT}; color:{PRIMARY_DARK}; font-weight:600;
        font-size:0.78rem; padding:6px 16px; border-radius:999px;
        letter-spacing:.02em; text-transform:uppercase;
    }}

    .fs-stat-box {{
        background:#FCF3F6; border-radius:14px; padding:16px 14px;
        text-align:left;
    }}
    .fs-stat-label {{ font-size:0.74rem; color:{INK_SOFT}; margin-bottom:6px; }}
    .fs-stat-value {{ font-family:'Poppins',sans-serif; font-weight:700; font-size:1.15rem; color:{INK}; }}

    .fs-hero {{
        background: linear-gradient(135deg, #FFF 0%, {PRIMARY_LIGHT} 100%);
        border-radius:22px; padding:34px 36px; border:1px solid #FBEAF0;
        margin-bottom:22px;
    }}

    .fs-btn-primary button {{
        background: linear-gradient(135deg,{PRIMARY} 0%, #E85D8C 100%) !important;
        color:#fff !important; border:none !important; border-radius:12px !important;
        font-weight:600 !important; padding:0.65rem 1.6rem !important;
        box-shadow: 0 8px 18px rgba(214,51,108,0.32) !important;
    }}

    .fs-status-badge {{
        display:inline-flex; align-items:center; gap:8px;
        padding:8px 18px; border-radius:12px; font-weight:700; font-size:1rem;
    }}

    .fs-step {{
        display:flex; flex-direction:column; align-items:center; text-align:center; flex:1;
    }}
    .fs-step-circle {{
        width:46px; height:46px; border-radius:50%; background:{PRIMARY_SOFT};
        color:{PRIMARY_DARK}; display:flex; align-items:center; justify-content:center;
        margin-bottom:8px; font-weight:700; font-family:'Poppins',sans-serif;
    }}
    .fs-step-circle.done {{ background:{PRIMARY}; color:#fff; }}
    .fs-step-title {{ font-size:0.82rem; font-weight:600; color:{INK}; }}
    .fs-step-sub {{ font-size:0.72rem; color:{INK_SOFT}; }}

    .fs-progress-track {{
        width:100%; height:8px; border-radius:999px; background:#F5E1E8; overflow:hidden;
    }}
    .fs-progress-fill {{ height:100%; border-radius:999px; }}

    .fs-feature-row {{
        display:flex; align-items:center; gap:14px; padding:10px 0;
        border-bottom:1px solid #F7EAEF;
    }}
    .fs-feature-row:last-child {{ border-bottom:none; }}

    .fs-badge-soft {{
        display:inline-block; padding:3px 10px; border-radius:8px; font-size:0.72rem; font-weight:600;
    }}

    /* Streamlit input tweaks */
    div[data-testid="stNumberInput"] input, div[data-baseweb="select"] {{
        border-radius:10px !important;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px 10px 0 0; padding: 8px 18px; font-weight:600; color:{INK_SOFT};
    }}
    .stTabs [aria-selected="true"] {{ color:{PRIMARY_DARK} !important; }}
    </style>
    """, unsafe_allow_html=True)


def sidebar_logo():
    st.markdown(f"""
    <div class="fs-logo-wrap">
        <div class="fs-logo-icon">{icon('hanger', 22, '#fff', 2)}</div>
        <div>
            <div class="fs-logo-title">FitSense</div>
            <div class="fs-logo-sub">Smart Clothing Size Predictor</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def card_open(title: str = None, icon_name: str = None):
    html = '<div class="fs-card">'
    if title:
        badge = f'<span class="fs-icon-badge">{icon(icon_name or "info", 17, "#B02154")}</span>' if icon_name else ""
        html += f'<div class="fs-card-title">{badge}{title}</div>'
    st.markdown(html, unsafe_allow_html=True)


def card_close():
    st.markdown('</div>', unsafe_allow_html=True)


def stat_box(label, value):
    st.markdown(f"""
    <div class="fs-stat-box">
        <div class="fs-stat-label">{label}</div>
        <div class="fs-stat-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)
