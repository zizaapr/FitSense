"""
icons.py
--------
Kumpulan ikon SVG inline (garis/stroke, bukan emoji) yang dipakai untuk
logo brand dan header tiap halaman, supaya tampil konsisten dan tetap
tajam di layar apa pun (tidak bergantung pada font emoji sistem).

Catatan penting: SVG mentah (<svg>...</svg>) yang ditempel langsung ke
st.markdown() sering TIDAK dirender sebagai gambar oleh Streamlit —
yang muncul malah teks atribut mentahnya (mis. `stroke="..." d="M8 3..."`)
karena indentasi string Python ikut dianggap blok kode oleh parser
Markdown. Solusinya sama seperti di utils/avatars.py: encode SVG ke
base64 lalu bungkus sebagai <img src="data:image/svg+xml;base64,...">.
"""

import base64

_SHIRT = """
<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none"
     stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="M8 3 4 6l1.2 3L8 8v11a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V8l2.8 1L20 6l-4-3-2 1.5a4 4 0 0 1-4 0L8 3Z"/>
</svg>
"""

_RULER = """
<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none"
     stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="m3.5 15.5 5-5 15 15-5 5Z"/>
  <path d="m6 13 2 2M9 10l2 2M12 7l2 2M15 4l2 2"/>
</svg>
"""

_CHART = """
<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none"
     stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 3v16a2 2 0 0 0 2 2h16"/>
  <path d="M7 15l4-4 3 3 5-6"/>
</svg>
"""

ICONS = {"shirt": _SHIRT, "ruler": _RULER, "chart": _CHART}


def icon_svg(name: str, size: int = 22, color: str = "currentColor") -> str:
    """Kembalikan markup SVG inline untuk ikon bernama `name`."""
    template = ICONS.get(name, _SHIRT)
    return template.format(size=size, color=color)


def icon_img(name: str, size: int = 22, color: str = "#1B2A4A") -> str:
    """Kembalikan tag <img> (SVG di-encode base64) untuk ikon bernama `name`.

    Dipakai sebagai pengganti `icon_svg()` di dalam st.markdown() supaya ikon
    benar-benar tampil sebagai gambar, bukan teks atribut SVG mentah.
    `currentColor` tidak didukung di dalam data-URI base64 yang berdiri
    sendiri, jadi warna default di sini memakai kode hex, bukan `currentColor`.
    """
    svg = icon_svg(name, size=size, color=color).strip()
    svg_b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return (
        f'<img src="data:image/svg+xml;base64,{svg_b64}" '
        f'width="{size}" height="{size}" alt="{name} icon"/>'
    )
