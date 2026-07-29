"""
icons.py
========
Kumpulan ikon SVG inline bergaya "line icon" (mirip Lucide/Feather).
Tidak memakai emoji sama sekali -- semua ikon di sidebar, kartu, dan
tombol memakai fungsi svg_icon() di bawah ini.
"""

_PATHS = {
    "home": '<path d="M3 11.5 12 4l9 7.5"/><path d="M5 10v9a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1v-9"/>',
    "ruler": '<path d="M3.5 8.5 8.5 3.5a2 2 0 0 1 2.8 0l9.2 9.2a2 2 0 0 1 0 2.8l-5 5a2 2 0 0 1-2.8 0L3.5 11.3a2 2 0 0 1 0-2.8Z"/><path d="m8 8 2 2M11 5l2 2M14 11l2 2M5 11l2 2"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 12h1v5h1"/>',
    "bar-chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "book-open": '<path d="M2 5.5C4 4 8 4 12 6c4-2 8-2 10-0.5v13C18 17 14 17 12 19c-2-2-6-2-10-0.5Z"/><path d="M12 6v13"/>',
    "circle-info": '<circle cx="12" cy="12" r="9"/><path d="M12 16v-4M12 8h.01"/>',
    "sparkles": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="m8 12.5 2.5 2.5L16 9.5"/>',
    "arrow-down-circle": '<circle cx="12" cy="12" r="9"/><path d="M12 8v7M9 12l3 3 3-3"/>',
    "arrow-up-circle": '<circle cx="12" cy="12" r="9"/><path d="M12 16V9M9 12l3-3 3 3"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "moon": '<path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5Z"/>',
    "layers": '<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 13 9 5 9-5"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "database": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "trending-up": '<path d="m3 17 6-6 4 4 8-8"/><path d="M17 7h4v4"/>',
    "shirt": '<path d="M8 3 4 6l1 4h2v11h10V10h2l1-4-4-3-2 2h-4Z"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-6 8-6s8 2 8 6"/>',
    "scale": '<path d="M12 3v18M6 7h12M4 7l2.5 6a2.5 2.5 0 0 0 5 0L14 7M14 7l2.5 6a2.5 2.5 0 0 0 5 0L24 7"/>',
    "wand": '<path d="m15 4 1.5 1.5M19 8l1.5 1.5M4 20 15 9M17 2l.5 2 2 .5-2 .5-.5 2-.5-2-2-.5 2-.5.5-2Z"/>',
    "gauge": '<path d="M12 15 15 9"/><circle cx="12" cy="15" r="1"/><path d="M4.6 17A9 9 0 1 1 19.4 17"/>',
    "help-circle": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 0 1 4.6 1.4c0 1.6-2.1 1.9-2.1 3.4M12 17h.01"/>',
    "graduation-cap": '<path d="m2 9 10-5 10 5-10 5-10-5Z"/><path d="M6 11v5c0 1.1 2.7 2 6 2s6-.9 6-2v-5"/><path d="M22 9v6"/>',
    "code": '<path d="m8 6-6 6 6 6M16 6l6 6-6 6"/>',
    "heart": '<path d="M12 20s-7-4.4-9.5-9C1 7.8 2.8 4 6.5 4 9 4 11 6 12 7.5 13 6 15 4 17.5 4 21.2 4 23 7.8 21.5 11 19 15.6 12 20 12 20Z"/>',
    "chevron-right": '<path d="m9 6 6 6-6 6"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "flag": '<path d="M5 3v18"/><path d="M5 4h11l-2 4 2 4H5"/>',
}


def svg_icon(name: str, size: int = 18, color: str = "currentColor", stroke_width: float = 2.0) -> str:
    """Mengembalikan string <svg> siap dipakai di st.markdown(..., unsafe_allow_html=True)."""
    path = _PATHS.get(name, _PATHS["circle-info"])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;flex-shrink:0;">{path}</svg>'
    )
