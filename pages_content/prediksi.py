import streamlit as st

from utils.preprocessing import (
    build_feature_row, predict, recommend_size, recommend_best_size,
    explain_prediction, SIZE_ORDER,
)
from utils.avatars import avatar_html, comparison_html
from utils.style import STATUS_COLORS, MUTED

BADGE_CLASS = {"Pas": "fs-badge-pas", "Terlalu Kecil": "fs-badge-kecil", "Terlalu Besar": "fs-badge-besar"}
BADGE_ICON = {"Pas": "✅", "Terlalu Kecil": "🔻", "Terlalu Besar": "🔺"}

EXPLANATION = {
    "Pas": "Berdasarkan hasil pengukuran tubuhmu, ukuran <b>{size}</b> memiliki kesesuaian yang baik di "
           "area bahu, dada, dan pinggang tidak terasa longgar maupun ketat secara berlebihan.",
    "Terlalu Kecil": "Berdasarkan hasil pengukuran tubuhmu, ukuran <b>{size}</b> cenderung lebih kecil "
                      "dibanding proporsi tubuhmu, sehingga berpotensi terasa sempit terutama di area "
                      "bahu, dada, atau pinggang.",
    "Terlalu Besar": "Berdasarkan hasil pengukuran tubuhmu, ukuran <b>{size}</b> cenderung lebih besar "
                      "dibanding proporsi tubuhmu, sehingga berpotensi terasa longgar dan kurang membentuk "
                      "badan.",
}

GENDER_KEY = {"Laki-laki": "male", "Perempuan": "female"}

# Legenda titik ukur: nomor cocok dengan badge pada diagram (lihat utils/avatars.py).
MEASUREMENT_LEGEND = [
    (1, "Lingkar Kepala", "Lingkar kepala, diukur melingkar tepat di atas alis dan telinga."),
    (2, "Lebar Bahu", "Jarak lurus antara ujung bahu kiri dan ujung bahu kanan."),
    (3, "Lebar/Lingkar Dada", "Lingkar dada, diukur melingkar pada bagian dada terlebar."),
    (4, "Lingkar Perut", "Lingkar perut, diukur melingkar pada bagian pusar."),
    (5, "Lingkar Pinggang", "Lingkar pinggang, diukur melingkar pada bagian pinggang tersempit."),
    (6, "Lingkar Pinggul", "Lingkar pinggul, diukur melingkar pada bagian pinggul terlebar."),
    (7, "Panjang Lengan", "Panjang lengan, dari ujung bahu hingga pergelangan tangan."),
    (8, "Bahu ke Pinggang", "Jarak dari titik bahu turun lurus hingga garis pinggang."),
    (9, "Pinggang ke Lutut", "Jarak dari garis pinggang turun lurus hingga lutut."),
    (10, "Panjang Kaki", "Panjang kaki, dari pinggul hingga mata kaki."),
    (11, "Tinggi Badan", "Tinggi badan tanpa alas kaki, dari ujung kepala hingga telapak kaki."),
]


def _clean(html: str) -> str:
    """Hapus leading whitespace tiap baris agar Markdown tidak salah mengira
    baris ber-indentasi sebagai code block (lihat catatan sama di beranda.py)."""
    return "\n".join(line.strip() for line in html.strip().splitlines())


def _icon(name: str) -> str:
    """Ikon garis 24x24 kecil untuk kartu ringkasan input (gaya sama dengan beranda._icon)."""
    icons = {
        "user": """<circle cx="12" cy="8" r="3.4" stroke-width="1.8"/>
            <path d="M5.5 20v-1.2A5.8 5.8 0 0 1 11.3 13h1.4a5.8 5.8 0 0 1 5.8 5.8V20" stroke-width="1.8"/>""",
        "ruler": """<rect x="3" y="8" width="18" height="8" rx="1.5" stroke-width="1.7" transform="rotate(-8 12 12)"/>
            <path d="M6.3 8.6 7.1 11.4M9.7 7.7 10.5 10.5M13.1 6.8 13.9 9.6M16.5 5.9 17.3 8.7"
                  stroke-width="1.4" stroke-linecap="round"/>""",
        "tag": """<path d="M20 13.2 12.8 20.4a2 2 0 0 1-2.8 0l-6.4-6.4a2 2 0 0 1-.6-1.4V5.5A1.5 1.5 0 0 1 4.5 4h7.1c.5 0 1 .2 1.4.6l6.4 6.4a2 2 0 0 1 .6 1.4c0 .5-.2 1-.6 1.4z" stroke-width="1.7" stroke-linejoin="round"/>
            <circle cx="8.2" cy="8.2" r="1.2" stroke-width="1.5"/>""",
    }
    return (
        f'<svg viewBox="0 0 24 24" fill="none" stroke="#1B2A4A" '
        f'stroke-linecap="round" stroke-linejoin="round">{icons[name]}</svg>'
    )


INPUT_OVERVIEW = [
    ("user", "#F4ECD8", "Data Diri", "Jenis Kelamin & Usia",
     "Dipakai untuk menyesuaikan avatar hasil prediksi dan mengelompokkan kategori usia "
     "(usia_group) sebagai salah satu fitur yang dipelajari model."),
    ("ruler", "#E9EBF3", "Pengukuran Tubuh", "11 Titik Ukur (satuan cm)",
     "Fitur utama model — menggambarkan bentuk & proporsi tubuhmu secara detail. Lihat diagram "
     "panduannya di bawah supaya hasil ukur akurat."),
    ("tag", "#F5E6E6", "Ukuran yang Dicoba", "S / M / L / XL / XXL",
     "Ukuran pakaian yang ingin kamu ketahui tingkat kecocokannya. Model akan membandingkan "
     "ukuran ini dengan hasil pengukuran tubuhmu di atas."),
]


def _render_input_overview():
    """Ringkasan singkat SEMUA jenis input pada form (bukan cuma titik ukur tubuh),
    supaya pengguna paham dulu apa saja yang akan diisi & untuk apa gunanya, sebelum
    scroll ke form yang panjang."""
    items_html = ""
    for icon_name, bg, label, value, desc in INPUT_OVERVIEW:
        items_html += f"""
            <div class="fs-model-item">
                <div class="fs-model-icon" style="background:{bg};">{_icon(icon_name)}</div>
                <div>
                    <div class="fs-model-label">{label}</div>
                    <div class="fs-model-value">{value}</div>
                    <div class="fs-model-desc">{desc}</div>
                </div>
            </div>
        """

    st.markdown(
        _clean(
            f"""
            <div class="fs-card">
                <div class="fs-section-title">📋 Apa Saja yang Perlu Disiapkan?</div>
                <p style="color:#5B6478; margin-top:-4px; margin-bottom:1.2rem;">
                    Formulir prediksi di bawah terdiri dari 3 kelompok input berikut. Semuanya
                    dipakai bersama oleh model untuk memprediksi tingkat kecocokan ukuran pakaianmu.
                </p>
                <div class="fs-model-grid">
                    {items_html}
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _render_intro():
    """Penjelasan (legenda) SEBELUM form diisi, supaya pengguna tidak bingung
    saat menginput karakteristik tubuhnya.

    Legenda ditampilkan sebagai GRID kartu kecil (bukan daftar 11 baris yang
    ditumpuk ke bawah, dan tanpa diagram siluet) supaya ringkas dan tetap enak
    dipindai matanya; setiap kartu langsung menampilkan penjelasan lengkapnya
    (bukan cuma judul + tooltip), supaya tetap terbaca jelas di HP yang tidak
    punya hover.
    """
    legend_html = ""
    for num, title, desc in MEASUREMENT_LEGEND:
        legend_html += f"""
            <div class="fs-legend-item">
                <div class="fs-legend-head">
                    <div class="fs-legend-num">{num}</div>
                    <div class="fs-legend-title">{title}</div>
                </div>
                <div class="fs-legend-desc">{desc}</div>
            </div>
        """

    st.markdown(
        _clean(
            f"""
            <div class="fs-card">
                <div class="fs-section-title">📖 Sebelum Mulai: Kenali Titik Ukurnya</div>
                <p style="color:#5B6478; margin-top:-4px; margin-bottom:1.2rem;">
                    Siapkan meteran kain, lalu ukur badanmu (satuan <b>cm</b>) sesuai penjelasan
                    tiap titik ukur di bawah ini. Ukur dalam posisi berdiri tegak, tanpa alas
                    kaki, dan gunakan pakaian tipis/ketat agar hasil ukur lebih akurat.
                </p>
                <div class="fs-legend-grid">{legend_html}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _measurement_input(label, key, default, help_text, col, min_v=None, max_v=250.0):
    """Input pengukuran dibiarkan KOSONG di awal (value=None, hanya diberi
    placeholder contoh angka) supaya:
    1. Kolom yang tidak diisi pengguna benar-benar bernilai None -> bisa
       divalidasi ("harap isi semua kolom") saat submit.
    2. Batas bawah (min_v) tidak dipasang di widget, supaya angka 0 / minus
       tetap bisa diketik pengguna, lalu ditangkap & ditolak oleh validasi
       kita sendiri (dengan pesan yang lebih jelas) alih-alih dibatasi diam-diam
       oleh Streamlit tanpa pesan.
    """
    return col.number_input(label, min_value=min_v, max_value=max_v, value=None,
                             step=0.5, help=help_text, key=key,
                             placeholder=f"Contoh: {default}")


def _render_form():
    st.markdown('<div class="fs-section-title">📝 Formulir Prediksi Ukuran</div>', unsafe_allow_html=True)
    with st.form("form_prediksi", clear_on_submit=False):

        st.markdown("**👤 Data Diri**")
        c1, c2 = st.columns(2)
        jenis_kelamin = c1.selectbox(
            "Jenis Kelamin", ["Laki-laki", "Perempuan"],
            help="Digunakan untuk menyesuaikan avatar hasil prediksi dan sebagai salah satu fitur model."
        )
        usia = c2.number_input(
            "Usia (tahun)", min_value=1, max_value=100, value=25, step=1,
            help="Usia kamu saat ini. Digunakan model untuk mengelompokkan kategori usia (usia_group)."
        )

        st.markdown('<div class="fs-divider"></div>', unsafe_allow_html=True)
        st.markdown("**📏 Pengukuran Tubuh Bagian Atas** (satuan cm)")
        c1, c2, c3 = st.columns(3)
        lingkar_kepala = _measurement_input("Lingkar Kepala", "lingkar_kepala", 56,
            "Lingkar kepala diukur melingkar di atas alis dan telinga.", c1)
        lebar_bahu = _measurement_input("Lebar Bahu", "lebar_bahu", 44,
            "Jarak horizontal antara ujung bahu kiri dan kanan.", c2)
        lebar_dada = _measurement_input("Lebar Dada", "lebar_dada", 90,
            "Lingkar dada diukur pada bagian dada terlebar.", c3)

        c1, c2, c3 = st.columns(3)
        lingkar_perut = _measurement_input("Lingkar Perut", "lingkar_perut", 80,
            "Lingkar perut diukur pada bagian pusar.", c1)
        lingkar_pinggang = _measurement_input("Lingkar Pinggang", "lingkar_pinggang", 78,
            "Lingkar pinggang diukur pada bagian pinggang tersempit.", c2)
        lingkar_pinggul = _measurement_input("Lingkar Pinggul", "lingkar_pinggul", 95,
            "Lingkar pinggul diukur pada bagian pinggul terlebar.", c3)

        c1, c2 = st.columns(2)
        panjang_lengan = _measurement_input("Panjang Lengan", "panjang_lengan", 58,
            "Panjang lengan diukur dari ujung bahu hingga pergelangan tangan.", c1)
        bahu_ke_pinggang = _measurement_input("Bahu ke Pinggang", "bahu_ke_pinggang", 42,
            "Jarak dari titik bahu hingga garis pinggang.", c2)

        st.markdown('<div class="fs-divider"></div>', unsafe_allow_html=True)
        st.markdown("**📐 Pengukuran Tubuh Bagian Bawah & Tinggi** (satuan cm)")
        c1, c2, c3 = st.columns(3)
        pinggang_ke_lutut = _measurement_input("Pinggang ke Lutut", "pinggang_ke_lutut", 55,
            "Jarak dari garis pinggang hingga lutut.", c1)
        panjang_kaki = _measurement_input("Panjang Kaki", "panjang_kaki", 95,
            "Panjang kaki diukur dari pinggul hingga mata kaki.", c2)
        tinggi_badan = _measurement_input("Tinggi Badan", "tinggi_badan", 165,
            "Tinggi badan diukur tanpa alas kaki, dari ujung kepala hingga telapak kaki.", c3)

        st.markdown('<div class="fs-divider"></div>', unsafe_allow_html=True)
        st.markdown("**👕 Ukuran yang Ingin Dicoba**")
        ukuran_dicoba = st.selectbox(
            "Pilih ukuran", SIZE_ORDER,
            index=1,
            help="Ukuran pakaian yang ingin kamu ketahui tingkat kecocokannya (S / M / L / XL / XXL)."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "Prediksi Ukuran", icon=":material/search:", use_container_width=True, type="primary"
        )

    if submitted:
        # Nama tampilan tiap kolom pengukuran, dipakai untuk pesan peringatan
        # yang menyebutkan kolom mana saja yang bermasalah.
        measurements = {
            "Lingkar Kepala": lingkar_kepala,
            "Lebar Bahu": lebar_bahu,
            "Lebar Dada": lebar_dada,
            "Lingkar Perut": lingkar_perut,
            "Lingkar Pinggang": lingkar_pinggang,
            "Lingkar Pinggul": lingkar_pinggul,
            "Panjang Lengan": panjang_lengan,
            "Bahu ke Pinggang": bahu_ke_pinggang,
            "Pinggang ke Lutut": pinggang_ke_lutut,
            "Panjang Kaki": panjang_kaki,
            "Tinggi Badan": tinggi_badan,
        }

        # 1) Validasi kolom kosong -> prediksi TIDAK diproses.
        empty_fields = [label for label, val in measurements.items() if val is None]
        if empty_fields:
            st.warning(
                "⚠️ Harap isi semua kolom pengukuran tubuh terlebih dahulu sebelum "
                f"melakukan prediksi. Kolom yang masih kosong: **{', '.join(empty_fields)}**."
            )
        else:
            # 2) Validasi nilai tidak masuk akal (0 atau minus) -> prediksi TIDAK diproses.
            invalid_fields = [label for label, val in measurements.items() if val <= 0]
            if invalid_fields:
                st.warning(
                    "⚠️ Ada nilai pengukuran yang tidak valid. Semua ukuran tubuh harus "
                    "lebih besar dari 0 cm (tidak boleh 0 atau minus). Kolom bermasalah: "
                    f"**{', '.join(invalid_fields)}**."
                )
            else:
                raw = dict(
                    jenis_kelamin=jenis_kelamin, usia=usia, lingkar_kepala=lingkar_kepala,
                    lebar_bahu=lebar_bahu, lebar_dada=lebar_dada, lingkar_perut=lingkar_perut,
                    lingkar_pinggang=lingkar_pinggang, lingkar_pinggul=lingkar_pinggul,
                    panjang_lengan=panjang_lengan, bahu_ke_pinggang=bahu_ke_pinggang,
                    pinggang_ke_lutut=pinggang_ke_lutut, panjang_kaki=panjang_kaki,
                    tinggi_badan=tinggi_badan, ukuran_dicoba=ukuran_dicoba,
                )
                st.session_state["fs_raw_input"] = raw
                st.session_state["fs_show_result"] = True
                st.rerun()


def _proba_bars(proba: dict, status: str):
    """Probabilitas tiap kelas ditampilkan sebagai bar horizontal yang
    ditumpuk ke bawah -- label di kiri, persentase di kanan (satu baris),
    lalu track penuh di bawahnya. Kelas hasil prediksi diberi label kecil
    'Prediksi' supaya langsung kelihatan pemenangnya."""
    rows_html = ""
    for label in ["Pas", "Terlalu Kecil", "Terlalu Besar"]:
        p = proba.get(label, 0.0)
        pct = p * 100
        color = STATUS_COLORS[label]
        is_active = label == status
        flag = f'<span class="fs-proba-bar-flag" style="background:{color};">Prediksi</span>' if is_active else ""
        label_style = f'color:{color} !important;' if is_active else ""
        rows_html += f"""
            <div class="fs-proba-bar-row">
                <div class="fs-proba-bar-head">
                    <span class="fs-proba-bar-label" style="{label_style}">{label} {flag}</span>
                    <span class="fs-proba-bar-pct">{pct:.1f}%</span>
                </div>
                <div class="fs-proba-bar-track">
                    <div class="fs-proba-bar-fill" style="width:{max(pct, 1.5):.1f}%; background:{color};"></div>
                </div>
            </div>
        """
    st.markdown(_clean(f'<div class="fs-proba-bar-list">{rows_html}</div>'), unsafe_allow_html=True)


STATUS_VERB = {
    "Pas": "mendukung ukuran ini dinilai <b>Pas</b>",
    "Terlalu Kecil": "membuat ukuran ini terasa <b>Terlalu Kecil</b>",
    "Terlalu Besar": "membuat ukuran ini terasa <b>Terlalu Besar</b>",
}


def _shap_narrative(contributions, status):
    """Rangkai kalimat penjelasan dari 3 faktor SHAP positif (paling
    mendorong ke arah hasil prediksi) yang paling besar pengaruhnya."""
    positives = sorted(
        (c for c in contributions if c["shap_value"] > 0),
        key=lambda c: c["shap_value"], reverse=True,
    )[:3]

    if not positives:
        return (
            "Tidak ada satu ukuran tubuh pun yang dominan di sini. Hasil ini "
            "merupakan gabungan pengaruh kecil dari beberapa ukuran tubuh sekaligus."
        )

    parts = [f"{c['label']} ({c['value_display']})" for c in positives]
    if len(parts) == 1:
        joined = parts[0]
    elif len(parts) == 2:
        joined = f"{parts[0]} dan {parts[1]}"
    else:
        joined = f"{', '.join(parts[:-1])}, dan {parts[-1]}"

    verb = STATUS_VERB.get(status, "memengaruhi hasil prediksi ini")
    return f"Faktor yang paling {verb} adalah <b>{joined}</b>."


def _shap_bars(contributions, status):
    """Render tiap fitur sebagai satu baris bar yang ditumpuk (diurutkan dari
    pengaruh terbesar ke terkecil, sesuai urutan `contributions`):
    - label fitur di kiri, nilai di kanan pada baris atas
    - bar menyimpang dari titik tengah track: warna status ke arah kanan
      = fitur mendorong ke arah hasil prediksi; abu-abu ke arah kiri
      = fitur justru menahan/menjauhkan hasil
    """
    max_abs = max((abs(c["shap_value"]) for c in contributions), default=0.0) or 1e-9
    push_color = STATUS_COLORS[status]

    st.markdown(
        f"""
        <div class="fs-shap-legend">
            <span><span class="fs-shap-dot" style="background:{push_color};"></span>Mendorong ke arah "{status}"</span>
            <span><span class="fs-shap-dot" style="background:{MUTED};"></span>Menahan / mengarah sebaliknya</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    rows_html = ""
    for c in contributions:
        val = c["shap_value"]
        pushing = val >= 0
        color = push_color if pushing else MUTED
        half_pct = max((abs(val) / max_abs) * 50, 4)
        left = 50.0 if pushing else 50.0 - half_pct
        rows_html += f"""
            <div class="fs-shap-row">
                <div class="fs-shap-row-top">
                    <span class="fs-shap-row-label">{c['label']}</span>
                    <span class="fs-shap-row-value">{c['value_display']}</span>
                </div>
                <div class="fs-shap-track">
                    <div class="fs-shap-fill" style="left:{left:.2f}%; width:{half_pct:.2f}%; background:{color};"></div>
                </div>
            </div>
        """

    st.markdown(_clean(f'<div class="fs-shap-rows">{rows_html}</div>'), unsafe_allow_html=True)


def _render_shap_section(raw, X, info, artifacts, status):
    """Bagian 'Kenapa Bisa Begini?' -- interpretasi SHAP dari hasil prediksi,
    menampilkan ukuran tubuh mana yang paling mempengaruhi status (Pas /
    Terlalu Kecil / Terlalu Besar) untuk baris input pengguna saat ini."""
    contributions = explain_prediction(raw, X, info, artifacts, status)

    st.markdown('<div class="fs-section-title">🔍 Faktor Paling Berpengaruh</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <p style="color:{MUTED}; margin-top:-6px; margin-bottom:1.1rem; font-size:0.88rem;">
            Ini bukan cuma angka probabilitas -- di bawah ini alasan model, ukuran
            tubuh mana yang paling berperan membuat hasilnya <b>{status}</b>,
            dihitung dengan metode SHAP.
        </p>
        """,
        unsafe_allow_html=True,
    )
    _shap_bars(contributions, status)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""<div class="fs-note-card" style="--note-color:{STATUS_COLORS[status]};">
            <div class="fs-note-icon">🔍</div>
            <div class="fs-note-text">{_shap_narrative(contributions, status)}</div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown('<div style="margin-bottom:1.7rem;"></div>', unsafe_allow_html=True)


def _render_result(artifacts):
    raw = st.session_state["fs_raw_input"]
    X, info = build_feature_row(raw, artifacts)
    result = predict(X, artifacts)

    status = result["status"]
    confidence = result["confidence"]
    proba = result["proba"]
    gender_key = GENDER_KEY.get(raw["jenis_kelamin"], "male")

    # (check) Cari ukuran yang PALING PAS secara langsung (coba semua ukuran
    # sekaligus), bukan cuma naik/turun 1 tingkat dari ukuran yang dicoba.
    best = recommend_best_size(raw, artifacts)
    rec_size = best["best_size"]

    if raw["ukuran_dicoba"] == rec_size and status == "Pas":
        rec_text = f"Ukuran {rec_size} yang kamu coba sudah pas di badanmu. Tidak perlu ganti ukuran."
    elif best["found_pas"]:
        rec_text = (
            f"Ukuran {raw['ukuran_dicoba']} yang kamu coba {status.lower()} untuk proporsi tubuhmu. "
            f"Ukuran yang paling pas adalah {rec_size} langsung coba ini, tidak perlu naik/turun bertahap."
        )
    else:
        # Tidak ada ukuran yang benar-benar "Pas" -> rec_size adalah yang paling mendekati
        rec_text = (
            f"Ukuran {raw['ukuran_dicoba']} yang kamu coba {status.lower()} untuk proporsi tubuhmu. "
            f"Dari semua pilihan ukuran, **{rec_size}** yang paling mendekati pas, meski belum sempurna."
        )

    st.markdown('<div class="fs-section-title">📸 Visualisasi Hasil Prediksi</div>', unsafe_allow_html=True)
    st.markdown(comparison_html(gender_key, status, width=150), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="text-align:center;">
            <span class="fs-badge {BADGE_CLASS[status]}">{BADGE_ICON[status]} {status}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div style="margin-bottom:1.7rem;"></div>', unsafe_allow_html=True)

    st.markdown('<div class="fs-section-title">🎯 Hasil Prediksi</div>', unsafe_allow_html=True)
    status_color = STATUS_COLORS[status]

    st.markdown(
        _clean(
            f"""
            <div class="fs-fit-profile">
                <div class="fs-fit-profile-tags">
                    <div class="fs-fit-tag">
                        <div class="fs-fit-tag-icon" style="background:#F4ECD8;">{_icon('user')}</div>
                        <div>
                            <div class="fs-fit-tag-label">Kategori Usia</div>
                            <div class="fs-fit-tag-value">{info['usia_group_label']}</div>
                        </div>
                    </div>
                    <div class="fs-fit-tag">
                        <div class="fs-fit-tag-icon" style="background:#E9EBF3;">{_icon('ruler')}</div>
                        <div>
                            <div class="fs-fit-tag-label">Kategori Tinggi</div>
                            <div class="fs-fit-tag-value">{info['kategori_tinggi_label']}</div>
                        </div>
                    </div>
                </div>
                <div class="fs-fit-profile-divider"></div>
                <div class="fs-fit-profile-confidence">
                    <div class="fs-confidence-ring" style="--pct:{confidence*100:.1f}; --ring-color:{status_color};">
                        <div class="fs-confidence-ring-inner">
                            <div class="fs-confidence-value">{confidence*100:.1f}%</div>
                        </div>
                    </div>
                    <div>
                        <div class="fs-info-pill-label" style="margin-bottom:4px;">Tingkat Keyakinan Model</div>
                        <div class="fs-confidence-caption">Model <b>{confidence*100:.1f}% yakin</b> dengan hasil prediksi <b>{status}</b> untuk ukuran ini.</div>
                    </div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="fs-subheading">📊 Probabilitas Tiap Kelas</div>', unsafe_allow_html=True)
    _proba_bars(proba, status)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        _clean(
            f"""
            <div class="fs-insight-duo">
                <div class="fs-insight-half" style="--insight-color:{status_color};">
                    <div class="fs-insight-head">
                        <div class="fs-insight-icon">💬</div>
                        <div class="fs-insight-title">Penjelasan Singkat</div>
                    </div>
                    <div class="fs-insight-text">{EXPLANATION[status].format(size=raw["ukuran_dicoba"])}</div>
                </div>
                <div class="fs-insight-half" style="--insight-color:{status_color};">
                    <div class="fs-insight-head">
                        <div class="fs-insight-icon">📌</div>
                        <div class="fs-insight-title">Rekomendasi Ukuran</div>
                    </div>
                    <div class="fs-insight-text">{rec_text}</div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    st.markdown('<div style="margin-bottom:1.7rem;"></div>', unsafe_allow_html=True)

    _render_shap_section(raw, X, info, artifacts, status)

    st.markdown('<div style="margin-top:1.3rem;"></div>', unsafe_allow_html=True)
    if st.button(
        "Prediksi Ulang", icon=":material/restart_alt:",
        use_container_width=True, type="primary",
    ):
        st.session_state["fs_show_result"] = False
        st.rerun()


def render(artifacts):
    if not st.session_state.get("fs_show_result", False):
        _render_input_overview()
        st.markdown("<br>", unsafe_allow_html=True)
        _render_intro()
        _render_form()
    else:
        _render_result(artifacts)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("✏️ Ubah data & prediksi lagi"):
            _render_form()
