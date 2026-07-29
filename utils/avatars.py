"""
avatars.py
-----------
Visual "human figure" untuk FitSense hasil prediksi.

Dua sumber gambar dipakai di sini, untuk tujuan berbeda:

1. FOTO ASLI (assets/avatars/*.png) -> dipakai untuk avatar HASIL PREDIKSI
   (avatar_html / comparison_html). Ada 6 foto: {male, female} x
   {Pas, Terlalu Kecil, Terlalu Besar}, di-crop dari bounding box yang SAMA
   supaya pose & skala konsisten waktu dibandingkan berdampingan. Badge
   status (centang / seru) ditumpuk di atasnya sebagai overlay HTML/CSS,
   bukan digambar ulang.
2. ILUSTRASI SVG (flat-vector, digambar lewat kode) -> tetap dipakai KHUSUS
   untuk diagram panduan titik ukur (get_measurement_guide_svg /
   measurement_guide_html), karena diagram itu perlu badge angka & garis
   pemandu yang presisi menempel ke bagian tubuh -- sesuatu yang sulit &
   rapuh kalau ditumpuk di atas foto asli.

Kepala, rambut, kaos, lengan, celana, dan sepatu pada ILUSTRASI SVG disusun
dari path/shape SVG (kurva bezier), lalu di-encode sebagai base64 data-URI
supaya konsisten dirender oleh Streamlit. FOTO ASLI juga dibungkus base64
data-URI dengan cara yang sama (lihat catatan di avatar_html).
"""

from __future__ import annotations

import base64
import os
from functools import lru_cache

# ----------------------------------------------------------------------------
# Foto avatar hasil prediksi (real photo, bukan ilustrasi)
# ----------------------------------------------------------------------------
_AVATAR_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "avatars")

AVATAR_PHOTO_FILE = {
    ("male", "Pas"): "male_pas.png",
    ("male", "Terlalu Kecil"): "male_kecil.png",
    ("male", "Terlalu Besar"): "male_besar.png",
    ("female", "Pas"): "female_pas.png",
    ("female", "Terlalu Kecil"): "female_kecil.png",
    ("female", "Terlalu Besar"): "female_besar.png",
}
# Rasio lebar:tinggi hasil crop foto (lihat assets/avatars/*.png) -- dipakai
# supaya <img> selalu punya width/height yang benar sebelum ter-load (no CLS).
# NB: avatar v2 (redesign) di-crop pada kanvas 273x726 (lihat scripts crop),
# beda proporsi dari foto lama (480x1208) -- rasio ini WAJIB ikut disesuaikan
# supaya <img> tidak stretch/gepeng.
AVATAR_PHOTO_RATIO = 726 / 273  # height / width


@lru_cache(maxsize=None)
def _avatar_photo_b64(gender: str, status: str) -> str:
    filename = AVATAR_PHOTO_FILE[(gender, status)]
    with open(os.path.join(_AVATAR_DIR, filename), "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")



# ----------------------------------------------------------------------------
# Palet warna (selaras dengan utils/style.py)
# ----------------------------------------------------------------------------
COLOR_BODY = "#E7D2B4"      # warna kulit netral/abstrak, senada kertas krem
COLOR_BODY_SHADE = "#D9BE9B"
COLOR_OUTLINE = "#1B2A4A"   # tinta navy
COLOR_PANTS = "#33415C"
COLOR_PANTS_SHADE = "#283349"
COLOR_NEUTRAL_TOP = "#EFE9DA"   # warna kaos netral untuk diagram panduan
COLOR_HAIR = "#1B2A4A"
COLOR_SHOE = "#0E1830"
COLOR_SHADOW = "#0E1830"

STATUS_COLOR = {
    "Pas": "#3E7D5A",               # benang hijau -> pas
    "Terlalu Kecil": "#B14D3D",     # benang merah bata -> kekecilan
    "Terlalu Besar": "#2E6E93",     # benang biru -> kebesaran
}

STATUS_BADGE_SYMBOL = {
    "Pas": "check",
    "Terlalu Kecil": "warning",
    "Terlalu Besar": "warning",
}

# ----------------------------------------------------------------------------
# Proporsi tubuh dasar per gender (dipakai status "Pas" sebagai baseline,
# lalu di-skala oleh FIT_SCALE untuk status lain). Inilah yang membuat siluet
# pria & wanita benar-benar beda bentuk, bukan cuma warna/aksesori.
# ----------------------------------------------------------------------------
# NB: hip_y (posisi pinggul/celana) TETAP di y=234 pada kanvas (lihat
# _figure_body), tidak bergantung pada gender/status. hem_y baseline "Pas"
# sengaja diset sedikit di atas hip_y (bukan menyentuhnya) supaya terlihat
# alami -- dan supaya status lain punya ruang untuk memendek/memanjang jelas.
HIP_Y = 234

BODY_BASE = {
    "male": dict(
        shoulder=52, chest=46, waist=44, hip=45,   # nyaris lurus (siluet "V" turun tipis)
        neck_half=16, sleeve_drop=48, hem_y=HIP_Y - 6, arm_w=18, leg_w=25, leg_gap=8,
    ),
    "female": dict(
        shoulder=42, chest=39, waist=31, hip=44,   # pinggang mengecil, pinggul melebar (jam pasir)
        neck_half=13, sleeve_drop=44, hem_y=HIP_Y - 2, arm_w=14, leg_w=19, leg_gap=10,
    ),
}

# Faktor skala relatif terhadap BODY_BASE untuk tiap status. `hem_shift` &
# `sleeve_shift` dalam satuan px absolut (bukan rasio) supaya efeknya jelas
# terlihat di kanvas manapun ukurannya. Hanya status "Terlalu Kecil" yang
# memunculkan skin-gap (lihat gating di get_avatar_svg / get_measurement_guide_svg).
FIT_SCALE = {
    "Pas": dict(
        shoulder=1.00, chest=1.00, waist=1.00, hem=1.00,
        hem_shift=0, sleeve_shift=0, wave=0,
    ),
    "Terlalu Kecil": dict(
        shoulder=0.86, chest=0.80, waist=0.74, hem=0.72,
        hem_shift=-48, sleeve_shift=-18, wave=0,
    ),
    "Terlalu Besar": dict(
        shoulder=1.30, chest=1.34, waist=1.36, hem=1.30,
        hem_shift=40, sleeve_shift=30, wave=7,
    ),
}


def _fit_params(gender: str, status: str) -> dict:
    """Gabungkan proporsi dasar gender + faktor skala status jadi satu set
    parameter siap pakai untuk menggambar kaos & badan."""
    base = BODY_BASE[gender]
    sc = FIT_SCALE[status]
    return dict(
        shoulder=base["shoulder"] * sc["shoulder"],
        chest=base["chest"] * sc["chest"],
        waist=base["waist"] * sc["waist"],
        hip=base["hip"],
        hem=base["hip"] * sc["hem"] + 6,
        hem_y=base["hem_y"] + sc["hem_shift"],
        sleeve_drop=base["sleeve_drop"] + sc["sleeve_shift"],
        sleeve_out=6 + max(0, sc["shoulder"] - 1) * 40,
        wave=sc["wave"],
        neck_half=base["neck_half"],
        arm_w=base["arm_w"],
        leg_w=base["leg_w"],
        leg_gap=base["leg_gap"],
    )


def _shirt_path(cx: float, top_y: float, p: dict) -> str:
    """Path 'd' SVG kaos memakai kurva bezier supaya siluetnya terasa seperti
    kain, bukan poligon kaku. Untuk wanita, sisi pinggang ditarik lebih masuk
    lalu melebar lagi ke hem supaya lekuk jam-pasir tetap kebaca di baju."""
    sh, sd, so = p["shoulder"], p["sleeve_drop"], p["sleeve_out"]
    ch, wa = p["chest"], p["waist"]
    hem, hem_y, wave = p["hem"], p["hem_y"], p["wave"]
    nh = p["neck_half"]
    chest_y = top_y + sd * 0.55
    waist_y = hem_y - 34
    sleeve_y = top_y + sd

    d = f"M {cx-nh:.1f},{top_y:.1f} "
    d += f"C {cx-sh*0.55:.1f},{top_y-2:.1f} {cx-sh:.1f},{top_y+2:.1f} {cx-sh:.1f},{top_y+10:.1f} "
    d += f"C {cx-sh-so:.1f},{top_y+sd*0.35:.1f} {cx-sh-so:.1f},{sleeve_y-8:.1f} {cx-sh-so*0.8:.1f},{sleeve_y:.1f} "
    d += f"C {cx-sh-so*0.3:.1f},{sleeve_y+4:.1f} {cx-ch-6:.1f},{chest_y+8:.1f} {cx-ch:.1f},{chest_y:.1f} "
    d += f"C {cx-ch+4:.1f},{chest_y+22:.1f} {cx-wa:.1f},{waist_y-16:.1f} {cx-wa:.1f},{waist_y:.1f} "
    d += f"C {cx-wa:.1f},{waist_y+14:.1f} {cx-hem+6:.1f},{hem_y-22:.1f} {cx-hem:.1f},{hem_y-6:.1f} "
    d += f"C {cx-hem:.1f},{hem_y:.1f} {cx-hem+2:.1f},{hem_y+wave:.1f} {cx-hem+10:.1f},{hem_y+wave*0.8:.1f} "
    d += f"Q {cx-hem*0.5:.1f},{hem_y-wave*0.5:.1f} {cx:.1f},{hem_y:.1f} "
    d += f"Q {cx+hem*0.5:.1f},{hem_y-wave*0.5:.1f} {cx+hem-10:.1f},{hem_y+wave*0.8:.1f} "
    d += f"C {cx+hem-2:.1f},{hem_y+wave:.1f} {cx+hem:.1f},{hem_y:.1f} {cx+hem:.1f},{hem_y-6:.1f} "
    d += f"C {cx+hem-6:.1f},{hem_y-22:.1f} {cx+wa:.1f},{waist_y+14:.1f} {cx+wa:.1f},{waist_y:.1f} "
    d += f"C {cx+wa:.1f},{waist_y-16:.1f} {cx+ch-4:.1f},{chest_y+22:.1f} {cx+ch:.1f},{chest_y:.1f} "
    d += f"C {cx+ch+6:.1f},{chest_y+8:.1f} {cx+sh+so*0.3:.1f},{sleeve_y+4:.1f} {cx+sh+so*0.8:.1f},{sleeve_y:.1f} "
    d += f"C {cx+sh+so:.1f},{sleeve_y-8:.1f} {cx+sh+so:.1f},{top_y+sd*0.35:.1f} {cx+sh:.1f},{top_y+10:.1f} "
    d += f"C {cx+sh:.1f},{top_y+2:.1f} {cx+sh*0.55:.1f},{top_y-2:.1f} {cx+nh:.1f},{top_y:.1f} "
    d += f"Q {cx:.1f},{top_y+12:.1f} {cx-nh:.1f},{top_y:.1f} Z"
    return d


def _skin_gap(cx: float, p: dict, gender: str, hip_y: float, status: str) -> str:
    """Untuk 'Terlalu Kecil': kaos memendek sampai perut/pinggang polos
    kelihatan (gap) sebelum garis celana -- ciri paling jelas kaos kekecilan.
    Tinggi gap dihitung DINAMIS sampai persis ke garis pinggul/celana (`hip_y`)
    supaya tidak ada area kosong (transparan) di antara hem kaos & celana."""
    if status != "Terlalu Kecil":
        return ""
    hem_y = p["hem_y"]
    if hem_y >= hip_y - 4:
        return ""
    top = hem_y
    bottom = hip_y + 6  # sedikit tumpang tindih dengan celana biar rapat
    half_top = p["waist"] * 0.92
    half_bottom = p["hip"] * 0.62
    mid = top + (bottom - top) * 0.5
    d = (
        f"M {cx-half_top:.1f},{top:.1f} "
        f"C {cx-half_top-2:.1f},{mid:.1f} {cx-half_bottom-2:.1f},{bottom-6:.1f} {cx-half_bottom:.1f},{bottom:.1f} "
        f"L {cx+half_bottom:.1f},{bottom:.1f} "
        f"C {cx+half_bottom+2:.1f},{bottom-6:.1f} {cx+half_top+2:.1f},{mid:.1f} {cx+half_top:.1f},{top:.1f} Z"
    )
    navel = "" if gender != "female" else (
        f'<ellipse cx="{cx:.1f}" cy="{bottom-8:.1f}" rx="2" ry="2.6" '
        f'fill="{COLOR_BODY_SHADE}" opacity="0.8"/>'
    )
    return (
        f'<path d="{d}" fill="{COLOR_BODY}" stroke="{COLOR_OUTLINE}" stroke-width="1.4"/>'
        f'{navel}'
    )


def _wrinkle_lines(status: str, cx: float, top_y: float, p: dict) -> str:
    """Detail tambahan: garis tarikan kain (kaos ketat) atau lipatan kain longgar."""
    if status == "Terlalu Kecil":
        y1 = top_y + p["sleeve_drop"] * 0.5
        y2 = p["hem_y"] - 16
        return f"""
        <line x1="{cx-p['chest']+5:.1f}" y1="{y1:.1f}" x2="{cx-p['chest']+16:.1f}" y2="{y1+13:.1f}"
              stroke="#7a2418" stroke-width="2" stroke-linecap="round" opacity="0.55"/>
        <line x1="{cx+p['chest']-5:.1f}" y1="{y1:.1f}" x2="{cx+p['chest']-16:.1f}" y2="{y1+13:.1f}"
              stroke="#7a2418" stroke-width="2" stroke-linecap="round" opacity="0.55"/>
        <line x1="{cx-p['waist']+2:.1f}" y1="{y2:.1f}" x2="{cx-p['waist']+13:.1f}" y2="{y2+10:.1f}"
              stroke="#7a2418" stroke-width="1.8" stroke-linecap="round" opacity="0.45"/>
        <line x1="{cx+p['waist']-2:.1f}" y1="{y2:.1f}" x2="{cx+p['waist']-13:.1f}" y2="{y2+10:.1f}"
              stroke="#7a2418" stroke-width="1.8" stroke-linecap="round" opacity="0.45"/>
        """
    if status == "Terlalu Besar":
        fy = top_y + p["sleeve_drop"] * 0.6
        return f"""
        <path d="M {cx-p['chest']*0.55:.1f} {fy:.1f} Q {cx-p['chest']*0.32:.1f} {fy+16:.1f} {cx-p['chest']*0.6:.1f} {fy+30:.1f}"
              fill="none" stroke="#123a63" stroke-width="2" stroke-linecap="round" opacity="0.4"/>
        <path d="M {cx+p['chest']*0.12:.1f} {fy+6:.1f} Q {cx+p['chest']*0.34:.1f} {fy+20:.1f} {cx+p['chest']*0.08:.1f} {fy+34:.1f}"
              fill="none" stroke="#123a63" stroke-width="2" stroke-linecap="round" opacity="0.4"/>
        <path d="M {cx-p['waist']*0.5:.1f} {p['hem_y']-46:.1f} Q {cx:.1f} {p['hem_y']-34:.1f} {cx+p['waist']*0.5:.1f} {p['hem_y']-46:.1f}"
              fill="none" stroke="#123a63" stroke-width="1.8" stroke-linecap="round" opacity="0.35"/>
        """
    return ""


def _hair(gender: str, cx: float) -> str:
    if gender == "male":
        # Rambut pendek: kubah rambut mengikuti lengkung kepala dengan tepi
        # (garis rambut) BERGELOMBANG -- bukan arc kedua yang polos, yang
        # dulu terbaca seperti headband/topi -- ditambah cambang tipis di
        # dua sisi telinga supaya jelas terbaca sebagai rambut.
        d_cap = (
            f"M {cx-30:.1f},46 "
            f"C {cx-31:.1f},23 {cx-17:.1f},7 {cx:.1f},7 "
            f"C {cx+17:.1f},7 {cx+31:.1f},23 {cx+30:.1f},46 "
            f"C {cx+26.5:.1f},39 {cx+23:.1f},45 {cx+18.5:.1f},37.5 "
            f"C {cx+14.5:.1f},44.5 {cx+8:.1f},40 {cx+5:.1f},33.5 "
            f"C {cx+2:.1f},40 {cx-3:.1f},40 {cx-6:.1f},33.5 "
            f"C {cx-9:.1f},40 {cx-15.5:.1f},44.5 {cx-19.5:.1f},37.5 "
            f"C {cx-24:.1f},45 {cx-27.5:.1f},39 {cx-30:.1f},46 Z"
        )
        sideburn_l = (
            f'<path d="M {cx-29.5:.1f},44 Q {cx-33:.1f},53 {cx-28.5:.1f},61 '
            f'Q {cx-25:.1f},53 {cx-26:.1f},44 Z" fill="{COLOR_HAIR}"/>'
        )
        sideburn_r = (
            f'<path d="M {cx+29.5:.1f},44 Q {cx+33:.1f},53 {cx+28.5:.1f},61 '
            f'Q {cx+25:.1f},53 {cx+26:.1f},44 Z" fill="{COLOR_HAIR}"/>'
        )
        return f"""
        {sideburn_l}{sideburn_r}
        <path d="{d_cap}" fill="{COLOR_HAIR}" stroke="{COLOR_OUTLINE}" stroke-width="1.5" stroke-linejoin="round"/>
        <path d="M {cx-22:.1f} 20 Q {cx-4:.1f} 9 {cx+8:.1f} 15" fill="none"
              stroke="#3a4d78" stroke-width="1.1" opacity="0.6" stroke-linecap="round"/>
        """
    # female: rambut menutupi atas kepala dengan tepi poni bergelombang (bukan
    # arc mulus) + belahan tengah, lalu juntai panjang melewati bahu kedua sisi.
    d_top = (
        f"M {cx-32:.1f},36 "
        f"C {cx-33:.1f},15 {cx-18:.1f},4 {cx:.1f},4 "
        f"C {cx+18:.1f},4 {cx+33:.1f},15 {cx+32:.1f},36 "
        f"C {cx+27:.1f},27 {cx+21:.1f},34 {cx+16:.1f},25 "
        f"C {cx+11:.1f},33 {cx+4:.1f},27 {cx:.1f},24 "
        f"C {cx-4:.1f},27 {cx-11:.1f},33 {cx-16:.1f},25 "
        f"C {cx-21:.1f},34 {cx-27:.1f},27 {cx-32:.1f},36 Z"
    )
    return f"""
    <path d="M {cx-33:.1f} 30 Q {cx:.1f} 6 {cx+33:.1f} 30 L {cx+37:.1f} 118 Q {cx+37:.1f} 130 {cx+25:.1f} 127
             L {cx+29:.1f} 46 Q {cx:.1f} 22 {cx-29:.1f} 46 L {cx-25:.1f} 127 Q {cx-37:.1f} 130 {cx-37:.1f} 118 Z"
          fill="{COLOR_HAIR}" stroke="{COLOR_OUTLINE}" stroke-width="1.5" stroke-linejoin="round"/>
    <path d="{d_top}" fill="{COLOR_HAIR}" stroke="{COLOR_OUTLINE}" stroke-width="1.3" stroke-linejoin="round"/>
    <path d="M {cx:.1f} 5 Q {cx:.1f} 18 {cx:.1f} 28" fill="none"
          stroke="#3a4d78" stroke-width="1" opacity="0.5"/>
    """


def _face(cx: float, cy: float, gender: str) -> str:
    lash = "" if gender != "female" else f"""
    <path d="M {cx-12.4:.1f} {cy-1.6:.1f} l -2.6 -1.6" stroke="{COLOR_OUTLINE}" stroke-width="1.1" stroke-linecap="round"/>
    <path d="M {cx+12.4:.1f} {cy-1.6:.1f} l 2.6 -1.6" stroke="{COLOR_OUTLINE}" stroke-width="1.1" stroke-linecap="round"/>
    """
    return f"""
    <circle cx="{cx:.1f}" cy="{cy:.1f}" r="30" fill="{COLOR_BODY}" stroke="{COLOR_OUTLINE}" stroke-width="1.8"/>
    <circle cx="{cx-10:.1f}" cy="{cy+1:.1f}" r="2.2" fill="{COLOR_OUTLINE}"/>
    <circle cx="{cx+10:.1f}" cy="{cy+1:.1f}" r="2.2" fill="{COLOR_OUTLINE}"/>
    {lash}
    <path d="M {cx-9:.1f} {cy+10:.1f} Q {cx:.1f} {cy+15:.1f} {cx+9:.1f} {cy+10:.1f}"
          fill="none" stroke="{COLOR_OUTLINE}" stroke-width="2" stroke-linecap="round"/>
    """


def _status_badge(status: str) -> str:
    color = STATUS_COLOR[status]
    bx, by = 196, 30
    if STATUS_BADGE_SYMBOL[status] == "check":
        icon = (f'<path d="M {bx-6} {by} l 4 4 l 9 -10" fill="none" stroke="{color}" '
                f'stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>')
    else:
        icon = (f'<line x1="{bx}" y1="{by-7}" x2="{bx}" y2="{by+3}" stroke="{color}" stroke-width="3.4" stroke-linecap="round"/>'
                f'<circle cx="{bx}" cy="{by+8}" r="1.8" fill="{color}"/>')
    return f"""
    <circle cx="{bx}" cy="{by}" r="16" fill="#FFFFFF" stroke="{color}" stroke-width="3"/>
    {icon}
    """


def _limb(x_top: float, y_top: float, w_top: float, x_bot: float, y_bot: float,
          w_bot: float, fill: str, radius: float = 7.0) -> str:
    """Anggota badan (lengan/kaki) berbentuk trapesium mengecil dengan ujung
    membulat -- terasa seperti bentuk tubuh asli, bukan kotak kaku."""
    d = (
        f"M {x_top-w_top/2:.1f},{y_top+radius:.1f} "
        f"Q {x_top-w_top/2:.1f},{y_top:.1f} {x_top-w_top/2+radius:.1f},{y_top:.1f} "
        f"L {x_top+w_top/2-radius:.1f},{y_top:.1f} "
        f"Q {x_top+w_top/2:.1f},{y_top:.1f} {x_top+w_top/2:.1f},{y_top+radius:.1f} "
        f"L {x_bot+w_bot/2:.1f},{y_bot-radius:.1f} "
        f"Q {x_bot+w_bot/2:.1f},{y_bot:.1f} {x_bot+w_bot/2-radius:.1f},{y_bot:.1f} "
        f"L {x_bot-w_bot/2+radius:.1f},{y_bot:.1f} "
        f"Q {x_bot-w_bot/2:.1f},{y_bot:.1f} {x_bot-w_bot/2:.1f},{y_bot-radius:.1f} Z"
    )
    return f'<path d="{d}" fill="{fill}" stroke="{COLOR_OUTLINE}" stroke-width="1.3" stroke-linejoin="round"/>'


def _figure_body(cx: float, top_y: float, p: dict, shirt_color: str,
                  gender: str, status: str, wrinkles: str = "",
                  skin_gap: str = "") -> str:
    """Susun satu figur lengkap (kaki, lengan, leher, kaos, kepala, rambut)
    memakai parameter siluet `p` (gender + status) dan warna kaos `shirt_color`."""
    leg_w, leg_gap = p["leg_w"], p["leg_gap"]
    arm_w = p["arm_w"] * (1.15 if status == "Terlalu Kecil" else 1.0)
    # Pinggul & kaki punya posisi TETAP di kanvas (tidak ikut geser walau hem
    # kaos memendek/memanjang jauh) -- supaya figur tidak pernah "kepotong"
    # di luar viewBox dan posisi celana selalu realistis di pinggul.
    hip_y = HIP_Y
    pants_top_y = HIP_Y - 12  # sedikit di atas hip_y supaya selalu tertutup rapi oleh hem kaos
    ankle_y = HIP_Y + 62
    lax = cx - leg_gap / 2 - leg_w
    rax = cx + leg_gap / 2

    # Lengan: mengikuti sleeve_drop (panjang) & posisi bahu, taper ke pergelangan.
    sh, sd = p["shoulder"], p["sleeve_drop"]
    shoulder_y = top_y + 14
    wrist_y = top_y + sd + 46
    lx_top, rx_top = cx - sh - 2, cx + sh + 2
    lx_bot, rx_bot = cx - sh * 0.62, cx + sh * 0.62
    shirt_d = _shirt_path(cx, top_y, p)

    return f"""
    <ellipse cx="{cx:.1f}" cy="310" rx="50" ry="7" fill="{COLOR_SHADOW}" opacity="0.08"/>
    {_limb(lax+leg_w/2, pants_top_y, leg_w, lax+leg_w/2 - (3 if gender=="female" else 0), ankle_y, leg_w*0.72, COLOR_PANTS)}
    {_limb(rax+leg_w/2, pants_top_y, leg_w, rax+leg_w/2 + (3 if gender=="female" else 0), ankle_y, leg_w*0.72, COLOR_PANTS)}
    <rect x="{lax-4:.1f}" y="{ankle_y-2:.1f}" width="{leg_w+8:.1f}" height="13" rx="6" fill="{COLOR_SHOE}"/>
    <rect x="{rax-4:.1f}" y="{ankle_y-2:.1f}" width="{leg_w+8:.1f}" height="13" rx="6" fill="{COLOR_SHOE}"/>
    {_limb(lx_top, shoulder_y, arm_w, lx_bot, wrist_y, arm_w*0.78, COLOR_BODY)}
    {_limb(rx_top, shoulder_y, arm_w, rx_bot, wrist_y, arm_w*0.78, COLOR_BODY)}
    <rect x="{cx-8:.1f}" y="82" width="16" height="18" rx="5" fill="{COLOR_BODY}" stroke="{COLOR_OUTLINE}" stroke-width="1.2"/>
    <path d="{shirt_d}" fill="{shirt_color}" stroke="{COLOR_OUTLINE}" stroke-width="1.8" stroke-linejoin="round"/>
    {skin_gap}
    {wrinkles}
    {_face(cx, 58, gender)}
    {_hair(gender, cx)}
    """


def get_avatar_svg(gender: str, status: str, width: int = 220) -> str:
    """
    Menghasilkan markup SVG ilustrasi hasil prediksi kecocokan ukuran, dengan
    siluet tubuh yang benar-benar berbeda antara pria/wanita dan bentuk kaos
    yang berbeda drastis antar status (Pas / Terlalu Kecil / Terlalu Besar).

    Parameters
    ----------
    gender : "male" | "female"
    status : "Pas" | "Terlalu Kecil" | "Terlalu Besar"
    width  : lebar tampilan dalam px (tinggi menyesuaikan rasio 240:320)
    """
    gender = "male" if str(gender).lower().startswith(("l", "m", "pria", "male")) else "female"
    if status not in STATUS_COLOR:
        status = "Pas"

    cx, top_y = 120, 96
    p = _fit_params(gender, status)
    shirt_color = STATUS_COLOR[status]
    wrinkles = _wrinkle_lines(status, cx, top_y, p)
    skin_gap = _skin_gap(cx, p, gender, hip_y=HIP_Y, status=status)
    body = _figure_body(cx, top_y, p, shirt_color, gender, status, wrinkles, skin_gap)
    badge = _status_badge(status)

    height = int(width * 320 / 240)
    svg = f"""
<svg width="{width}" height="{height}" viewBox="0 0 240 320" xmlns="http://www.w3.org/2000/svg">
  {body}
  {badge}
</svg>
"""
    return svg.strip()


def _guide_badge(number: int, x: float, y: float) -> str:
    return f"""
    <circle cx="{x}" cy="{y}" r="12" fill="#FFFFFF" stroke="{COLOR_OUTLINE}" stroke-width="1.8"/>
    <text x="{x}" y="{y+1}" text-anchor="middle" dominant-baseline="central"
          font-family="'IBM Plex Mono', monospace" font-size="12.5" font-weight="700"
          fill="{COLOR_OUTLINE}">{number}</text>
    """


def _guide_lead(x1: float, y1: float, x2: float, y2: float) -> str:
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{COLOR_OUTLINE}" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.5"/>')


def get_measurement_guide_svg(width: int = 230, gender: str = "male") -> str:
    """
    Diagram panduan titik ukur tubuh (11 titik bernomor), memakai figur
    ilustrasi YANG SAMA dengan avatar hasil prediksi (siluet kaos netral,
    tanpa status) supaya tampilan sebelum & sesudah form konsisten -- dan
    siluetnya tetap mengikuti bentuk tubuh gender yang dipilih.

    Nomor 1-11 mengikuti urutan field pada form:
    1 lingkar kepala, 2 lebar bahu, 3 lebar/lingkar dada, 4 lingkar perut,
    5 lingkar pinggang, 6 lingkar pinggul, 7 panjang lengan,
    8 bahu ke pinggang, 9 pinggang ke lutut, 10 panjang kaki, 11 tinggi badan.
    """
    gender = "male" if str(gender).lower().startswith(("l", "m", "pria", "male")) else "female"
    cx, top_y = 150, 116
    p = _fit_params(gender, "Pas")
    body = _figure_body(cx, top_y, p, COLOR_NEUTRAL_TOP, gender, "Pas")

    svg = f"""
<svg width="{width}" height="{int(width*380/300)}" viewBox="0 0 300 380" xmlns="http://www.w3.org/2000/svg">
  <g transform="translate(30,20)">
    {body}

    <!-- garis tinggi badan (11) di tepi kiri -->
    <line x1="-22" y1="18" x2="-22" y2="300" stroke="{COLOR_OUTLINE}" stroke-width="1.2" opacity="0.45"/>
    <line x1="-26" y1="18" x2="-18" y2="18" stroke="{COLOR_OUTLINE}" stroke-width="1.2" opacity="0.45"/>
    <line x1="-26" y1="300" x2="-18" y2="300" stroke="{COLOR_OUTLINE}" stroke-width="1.2" opacity="0.45"/>

    <!-- badge kanan: 2 bahu, 3 dada, 4 perut, 5 pinggang, 6 pinggul -->
    {_guide_lead(cx+66, 108, cx+40, 100)}
    {_guide_badge(2, cx+78, 108)}
    {_guide_lead(cx+66, 138, cx+42, 138)}
    {_guide_badge(3, cx+78, 138)}
    {_guide_lead(cx+66, 163, cx+38, 163)}
    {_guide_badge(4, cx+78, 163)}
    {_guide_lead(cx+66, 188, cx+34, 188)}
    {_guide_badge(5, cx+78, 188)}
    {_guide_lead(cx+66, 213, cx+40, 213)}
    {_guide_badge(6, cx+78, 213)}

    <!-- badge kiri: 11 tinggi, 1 kepala, 8 bahu-pinggang, 7 lengan, 9 pinggang-lutut, 10 kaki -->
    {_guide_lead(cx-78, 14, cx-42, 40)}
    {_guide_badge(11, cx-90, 14)}
    {_guide_lead(cx-78, 48, cx-32, 58)}
    {_guide_badge(1, cx-90, 48)}
    {_guide_lead(cx-78, 150, cx-46, 150)}
    {_guide_badge(8, cx-90, 150)}
    {_guide_lead(cx-78, 175, cx-63, 175)}
    {_guide_badge(7, cx-90, 175)}
    {_guide_lead(cx-78, 240, cx-50, 240)}
    {_guide_badge(9, cx-90, 240)}
    {_guide_lead(cx-78, 270, cx-45, 270)}
    {_guide_badge(10, cx-90, 270)}
  </g>
</svg>
"""
    return svg.strip()


def measurement_guide_html(width: int = 230, gender: str = "male") -> str:
    """Bungkus diagram panduan pengukuran sebagai <img> data-URI (lihat catatan di avatar_html)."""
    svg = get_measurement_guide_svg(width=width, gender=gender)
    svg_b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    height = int(width * 380 / 300)
    return (
        f'<div class="fs-avatar-wrap">'
        f'<img src="data:image/svg+xml;base64,{svg_b64}" '
        f'width="{width}" height="{height}" alt="Diagram panduan titik ukur tubuh"/>'
        f'</div>'
    )


COMPARE_ORDER = ["Terlalu Kecil", "Pas", "Terlalu Besar"]

COMPARE_DESC = {
    "Terlalu Kecil": "Pakaian terasa ketat",
    "Pas": "Ukuran pas di tubuh",
    "Terlalu Besar": "Pakaian terasa longgar",
}


def _clean(html: str) -> str:
    """Hapus leading whitespace tiap baris supaya Markdown/Streamlit tidak
    salah mengira baris ber-indentasi sebagai code block (lihat catatan
    sama di pages_content/prediksi.py)."""
    return "\n".join(line.strip() for line in html.strip().splitlines())


def comparison_html(gender: str, active_status: str, width: int = 150) -> str:
    """Bungkus 3 avatar (Terlalu Kecil / Pas / Terlalu Besar) berdampingan,
    dengan panel status hasil prediksi ditonjolkan (border + latar warna
    status) -- dipakai di hasil prediksi supaya pengguna langsung bisa
    membandingkan ketiga kemungkinan, bukan cuma melihat satu ukuran saja."""
    if active_status not in STATUS_COLOR:
        active_status = "Pas"
    items = []
    for status in COMPARE_ORDER:
        color = STATUS_COLOR[status]
        is_active = status == active_status
        active_cls = " fs-compare-active" if is_active else ""
        avatar = avatar_html(gender, status, width=width)
        items.append(
            _clean(
                f"""
                <div class="fs-compare-item{active_cls}" style="--fs-compare-color:{color};">
                    <div class="fs-compare-title" style="color:{color};">{status}</div>
                    <div class="fs-compare-desc">{COMPARE_DESC[status]}</div>
                    {avatar}
                </div>
                """
            )
        )
    return f'<div class="fs-compare-grid">{"".join(items)}</div>'


def _avatar_badge_html(status: str) -> str:
    """Badge status (centang hijau / seru merah-biru) ditumpuk di pojok kanan
    atas foto avatar, ditulis pakai HTML/CSS murni (bukan SVG) supaya tetap
    ringan & konsisten ditumpuk di atas <img> foto."""
    color = STATUS_COLOR[status]
    symbol = "\u2713" if STATUS_BADGE_SYMBOL[status] == "check" else "!"
    return (
        f'<div class="fs-avatar-badge" style="--fs-badge-color:{color};">'
        f'<span>{symbol}</span></div>'
    )


def avatar_html(gender: str, status: str, width: int = 210) -> str:
    """Bungkus foto avatar asli (real photo) sebagai <img> data-URI + badge
    status overlay, di dalam wrapper <div> berclass CSS.

    Foto disimpan sebagai file PNG statis di assets/avatars/ (bukan
    digambar ulang tiap render seperti ilustrasi SVG) -- lihat
    AVATAR_PHOTO_FILE. Tetap dibungkus base64 data-URI (bukan path file
    langsung) karena itu format yang paling konsisten dirender oleh
    Streamlit lewat st.markdown(unsafe_allow_html=True).
    """
    gender = "male" if str(gender).lower().startswith(("l", "m", "pria", "male")) else "female"
    if status not in STATUS_COLOR:
        status = "Pas"

    photo_b64 = _avatar_photo_b64(gender, status)
    height = int(width * AVATAR_PHOTO_RATIO)
    badge = _avatar_badge_html(status)
    return (
        f'<div class="fs-avatar-wrap">'
        f'<div class="fs-avatar-photo" style="width:{width}px;">'
        f'<img src="data:image/png;base64,{photo_b64}" '
        f'width="{width}" height="{height}" alt="Avatar hasil prediksi ukuran"/>'
        f'{badge}'
        f'</div>'
        f'</div>'
    )
