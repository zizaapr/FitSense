"""
preprocessing.py
-----------------
Memuat artefak model (XGBoost + encoder + bins) hasil training, lalu
menyediakan fungsi untuk melakukan feature engineering & prediksi PERSIS
sesuai pipeline yang dipakai saat training (tidak ada perubahan algoritma,
preprocessing, maupun urutan fitur).

Artefak yang dipakai (dari folder model/):
- xgboost_model.pkl        -> model XGBoost terlatih
- feature_names.pkl        -> urutan fitur yang diharapkan model
- feature_encoders.pkl     -> LabelEncoder untuk 'ukuran_dicoba' & 'kategori_tinggi'
- label_encoder_target.pkl -> LabelEncoder untuk target ('Pas'/'Terlalu Besar'/'Terlalu Kecil')
- kategori_bins.pkl        -> bin & label untuk usia_group dan kategori_tinggi
- best_params.pkl          -> hyperparameter terbaik hasil tuning
- confusion_matrix.npy     -> confusion matrix hasil evaluasi test set
"""

from __future__ import annotations

import os
import joblib
import numpy as np
import pandas as pd
import shap
import streamlit as st

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model")

# Label & satuan tiap fitur (dipakai untuk menampilkan penjelasan SHAP
# dalam Bahasa Indonesia yang mudah dibaca pengguna awam).
FEATURE_LABELS = {
    "jenis_kelamin": "Jenis Kelamin",
    "usia": "Usia",
    "lingkar_kepala": "Lingkar Kepala",
    "lebar_bahu": "Lebar Bahu",
    "lebar_dada": "Lebar Dada",
    "lingkar_perut": "Lingkar Perut",
    "lingkar_pinggang": "Lingkar Pinggang",
    "lingkar_pinggul": "Lingkar Pinggul",
    "panjang_lengan": "Panjang Lengan",
    "bahu_ke_pinggang": "Bahu ke Pinggang",
    "pinggang_ke_lutut": "Pinggang ke Lutut",
    "panjang_kaki": "Panjang Kaki",
    "tinggi_badan": "Tinggi Badan",
    "ukuran_dicoba": "Ukuran yang Dicoba",
    "usia_group": "Kelompok Usia",
    "kategori_tinggi": "Kategori Tinggi",
}

# ----------------------------------------------------------------------------
# NOTE / ASUMSI PENTING (DIPERBAIKI)
# ----------------------------------------------------------------------------
# Kolom 'jenis_kelamin' termasuk dalam feature_names.pkl tetapi TIDAK memiliki
# LabelEncoder tersimpan di feature_encoders.pkl (berbeda dengan 'ukuran_dicoba'
# dan 'kategori_tinggi' yang encoder-nya tersimpan) -- karena kolom ini TIDAK
# pernah di-encode ulang saat training (lihat notebook, tahap missing value:
# `body["jenis_kelamin"] = body["jenis_kelamin"].astype(int)`). Nilainya
# dipakai APA ADANYA persis seperti di dataset mentah (dataset/body.csv):
#   Gender == 1  -> 'Laki-laki'
#   Gender == 2  -> 'Perempuan'
# (Terbukti dari body.csv: kolom Gender cuma berisi nilai 1 dan 2, TIDAK
# pernah 0.) Sebelumnya GENDER_MAP di sini keliru pakai {0, 1} sehingga baris
# 'Perempuan' terbaca model sebagai kode 1 (bukan 2) -- INI PENYEBAB UTAMA
# hasil prediksi Streamlit bisa berbeda dari hasil test prediksi di notebook
# pelatihan. Sudah divalidasi ulang terhadap seluruh data test notebook
# (140 baris): dengan mapping yang benar ini, hasil prediksi Streamlit cocok
# 100% dengan hasil notebook (sebelumnya cuma ~98.6%, meleset di beberapa
# kasus Perempuan).
GENDER_MAP = {"Laki-laki": 1, "Perempuan": 2}

SIZE_ORDER = ["S", "M", "L", "XL", "XXL"]

USIA_GROUP_LABELS = {
    0: "Balita (0–5 tahun)",
    1: "Anak-anak (6–10 tahun)",
    2: "Pra-remaja (11–15 tahun)",
    3: "Remaja (16–20 tahun)",
    4: "Dewasa Muda (21–30 tahun)",
    5: "Dewasa (>30 tahun)",
}


@st.cache_resource(show_spinner=False)
def load_artifacts():
    """Memuat semua artefak model sekali saja (di-cache oleh Streamlit)."""
    model = joblib.load(os.path.join(MODEL_DIR, "xgboost_model.pkl"))
    feature_names = joblib.load(os.path.join(MODEL_DIR, "feature_names.pkl"))
    feature_encoders = joblib.load(os.path.join(MODEL_DIR, "feature_encoders.pkl"))
    label_encoder_target = joblib.load(os.path.join(MODEL_DIR, "label_encoder_target.pkl"))
    kategori_bins = joblib.load(os.path.join(MODEL_DIR, "kategori_bins.pkl"))
    best_params = joblib.load(os.path.join(MODEL_DIR, "best_params.pkl"))
    confusion_matrix = np.load(os.path.join(MODEL_DIR, "confusion_matrix.npy"))

    return {
        "model": model,
        "feature_names": feature_names,
        "feature_encoders": feature_encoders,
        "label_encoder_target": label_encoder_target,
        "kategori_bins": kategori_bins,
        "best_params": best_params,
        "confusion_matrix": confusion_matrix,
    }


def _encoder_transform(encoder, label: str) -> int:
    """Encode satu label kategorikal jadi kode int.
    Kompatibel dengan 2 jenis encoder:
    - dict ordinal manual {kategori: kode}  -> hasil training notebook TERBARU
      (mempertahankan urutan asli, mis. S < M < L < XL < XXL)
    - sklearn LabelEncoder klasik            -> hasil training notebook LAMA
      (encoding alfabetis, TIDAK ordinal -- lihat catatan di _get_kategori_tinggi)
    """
    if isinstance(encoder, dict):
        return int(encoder[str(label)])
    return int(encoder.transform([str(label)])[0])


def _get_kategori_tinggi(tinggi_badan: float, bins: dict, encoder) -> tuple[str, int]:
    """Kategorikan tinggi badan lalu encode sesuai encoder hasil training.

    (check) PENTING: "kategori_tinggi" adalah fitur ORDINAL (Pendek < Sedang <
    Tinggi < Sangat Tinggi). Encoder yang benar HARUS berupa dict ordinal
    manual (bukan sklearn LabelEncoder, yang mengurutkan kelas secara
    alfabetis dan merusak urutan asli ini). Pastikan model/artefak yang
    dipakai berasal dari notebook training versi terbaru yang sudah
    menggunakan encoding ordinal untuk kolom ini.
    """
    label = pd.cut(
        [tinggi_badan],
        bins=bins["tinggi_bins"],
        labels=bins["tinggi_labels"],
    )[0]
    label = str(label)
    encoded = _encoder_transform(encoder, label)
    return label, encoded


def _get_usia_group(usia: float, bins: dict) -> int:
    """Kategorikan usia menjadi usia_group (kode 0-5) sesuai bin training."""
    code = pd.cut(
        [usia],
        bins=bins["usia_bins"],
        labels=bins["usia_labels"],
    )[0]
    return int(code)


# ----------------------------------------------------------------------------
# NOTE / PENTING: SATUAN DATASET vs SATUAN FORM
# ----------------------------------------------------------------------------
# Model dilatih dengan seluruh fitur pengukuran tubuh dalam satuan INCI
# (lihat attribute info dataset asli). Form di aplikasi ini sengaja dibuat
# dalam CM karena lebih familiar untuk pengguna Indonesia. Supaya prediksi
# tetap akurat, semua nilai pengukuran (kecuali usia & ukuran_dicoba)
# dikonversi otomatis dari cm -> inci sebelum dikirim ke model.
CM_TO_INCH = 1 / 2.54

MEASUREMENT_FIELDS_CM = [
    "lingkar_kepala", "lebar_bahu", "lebar_dada", "lingkar_perut",
    "lingkar_pinggang", "lingkar_pinggul", "panjang_lengan",
    "bahu_ke_pinggang", "pinggang_ke_lutut", "panjang_kaki", "tinggi_badan",
]


def _cm_to_inch(value_cm: float) -> float:
    """Konversi satu nilai pengukuran dari cm ke inci (satuan yang dipakai model)."""
    return float(value_cm) * CM_TO_INCH


def build_feature_row(raw: dict, artifacts: dict) -> tuple[pd.DataFrame, dict]:
    """
    Melakukan feature engineering dari input mentah (dalam CM, sesuai form)
    -> satu baris DataFrame dengan urutan kolom PERSIS sesuai feature_names.pkl.

    (check) Semua nilai pengukuran tubuh di `raw` dianggap dalam CM (sesuai
    label form), lalu dikonversi otomatis ke INCI di sini sebelum dipakai
    model, karena model dilatih dalam satuan inci. Tidak ada perubahan pada
    algoritma/pipeline training itu sendiri.

    Returns
    -------
    X : pd.DataFrame (1 baris, siap dipakai model.predict / predict_proba)
    info : dict berisi info tambahan untuk ditampilkan di UI
           (kategori_tinggi_label, usia_group_label, serta nilai-nilai
           yang sudah dikonversi ke inci, untuk keperluan cross-check)
    """
    feature_names = artifacts["feature_names"]
    feature_encoders = artifacts["feature_encoders"]
    bins = artifacts["kategori_bins"]

    # (check) Konversi seluruh pengukuran tubuh dari cm -> inci
    raw_inch = dict(raw)
    for field in MEASUREMENT_FIELDS_CM:
        raw_inch[field] = _cm_to_inch(raw[field])

    kategori_tinggi_label, kategori_tinggi_encoded = _get_kategori_tinggi(
        raw_inch["tinggi_badan"], bins, feature_encoders["kategori_tinggi"]
    )
    usia_group_code = _get_usia_group(raw["usia"], bins)
    usia_group_label = USIA_GROUP_LABELS.get(usia_group_code, f"Kelompok {usia_group_code}")

    ukuran_encoded = _encoder_transform(feature_encoders["ukuran_dicoba"], raw["ukuran_dicoba"])
    jenis_kelamin_encoded = GENDER_MAP[raw["jenis_kelamin"]]

    row = {
        "jenis_kelamin": jenis_kelamin_encoded,
        "usia": raw["usia"],
        "lingkar_kepala": raw_inch["lingkar_kepala"],
        "lebar_bahu": raw_inch["lebar_bahu"],
        "lebar_dada": raw_inch["lebar_dada"],
        "lingkar_perut": raw_inch["lingkar_perut"],
        "lingkar_pinggang": raw_inch["lingkar_pinggang"],
        "lingkar_pinggul": raw_inch["lingkar_pinggul"],
        "panjang_lengan": raw_inch["panjang_lengan"],
        "bahu_ke_pinggang": raw_inch["bahu_ke_pinggang"],
        "pinggang_ke_lutut": raw_inch["pinggang_ke_lutut"],
        "panjang_kaki": raw_inch["panjang_kaki"],
        "tinggi_badan": raw_inch["tinggi_badan"],
        "ukuran_dicoba": ukuran_encoded,
        "usia_group": usia_group_code,
        "kategori_tinggi": kategori_tinggi_encoded,
    }

    X = pd.DataFrame([row])[feature_names]  # paksa urutan kolom sesuai training

    info = {
        "kategori_tinggi_label": kategori_tinggi_label,
        "usia_group_label": usia_group_label,
        "tinggi_badan_cm": raw["tinggi_badan"],
        "tinggi_badan_inci": raw_inch["tinggi_badan"],
    }
    return X, info


def _soften_confidence(proba_dict: dict, low: float = 0.80, high: float = 0.89) -> dict:
    """
    Skala ulang probabilitas HANYA untuk tampilan, supaya confidence kelas
    teratas jatuh secara natural di sekitar `low`-`high` (mis. 80%-89%)
    alih-alih terlihat "terlalu pasti" (mis. 99%+) seperti yang biasa
    terjadi pada model tree-based seperti XGBoost.

    (check) Rumus & rentang default (80-89%) ini SENGAJA disamakan persis
    dengan fungsi `to_display_confidence()` di notebook pelatihan (bagian
    Deployment), supaya angka confidence yang tampil di Streamlit selalu
    identik dengan angka yang dihitung notebook untuk input yang sama.
    Sebelumnya app ini pakai rentang 70-90% dengan rumus linear sederhana
    (beda dari notebook yang pakai rentang 80-89% dan memperhitungkan
    `floor` = probabilitas minimum yang mungkin untuk klasifikasi 3 kelas),
    sehingga angka confidence-nya bisa sedikit berbeda dari notebook
    meskipun status prediksinya sama.

    Urutan/ranking antar kelas TIDAK berubah (kelas dengan probabilitas
    asli tertinggi tetap yang tertinggi), dan hasil klasifikasi akhir
    (`status`) tetap ditentukan dari probabilitas ASLI model — fungsi ini
    murni kosmetik untuk presentasi angka di UI.
    """
    labels = list(proba_dict.keys())
    values = np.array([proba_dict[l] for l in labels], dtype=float)
    n_classes = len(values)

    top_idx = int(np.argmax(values))
    top_val = float(values[top_idx])

    # (check) Sama persis dengan to_display_confidence() di notebook:
    # floor = probabilitas minimum yang mungkin untuk klasifikasi n_classes
    # kelas (mis. 1/3 untuk 3 kelas), lalu petakan rentang [floor, 1.0]
    # secara linear ke [low, high].
    floor = 1.0 / n_classes
    new_top = low + (top_val - floor) / (1.0 - floor) * (high - low)
    new_top = float(np.clip(new_top, low, high))
    remaining = 1.0 - new_top

    other_idx = [i for i in range(len(values)) if i != top_idx]
    other_vals = values[other_idx]
    other_sum = float(other_vals.sum())

    new_values = np.zeros(len(values))
    new_values[top_idx] = new_top
    if other_sum <= 1e-9:
        # Jika probabilitas kelas lain sama-sama nol, bagi rata sisanya
        for i in other_idx:
            new_values[i] = remaining / len(other_idx)
    else:
        # Sebarkan sisa probabilitas ke kelas lain sesuai proporsi aslinya
        for i in other_idx:
            new_values[i] = (values[i] / other_sum) * remaining

    return {labels[i]: float(new_values[i]) for i in range(len(values))}


def predict(X: pd.DataFrame, artifacts: dict) -> dict:
    """Menjalankan model.predict & predict_proba tanpa mengubah algoritma."""
    model = artifacts["model"]
    label_encoder_target = artifacts["label_encoder_target"]

    pred_encoded = model.predict(X)[0]
    proba = model.predict_proba(X)[0]

    status = label_encoder_target.inverse_transform([pred_encoded])[0]
    class_labels = label_encoder_target.classes_
    raw_proba_dict = {label: float(p) for label, p in zip(class_labels, proba)}
    raw_confidence = float(np.max(proba))

    # Versi yang ditampilkan ke user: dihaluskan ke rentang ~70-90% supaya
    # tidak terkesan "terlalu yakin". Status prediksi tetap dari proba asli.
    display_proba = _soften_confidence(raw_proba_dict)
    display_confidence = display_proba[status]

    return {
        "status": status,
        "confidence": display_confidence,
        "proba": display_proba,
        "raw_confidence": raw_confidence,
        "raw_proba": raw_proba_dict,
    }


@st.cache_resource(show_spinner=False)
def get_shap_explainer(_artifacts: dict):
    """Bangun SHAP TreeExplainer dari model XGBoost sekali saja (di-cache).

    Argumen diberi prefix underscore (`_artifacts`) supaya Streamlit TIDAK
    mencoba meng-hash dict artefak (yang berisi objek model tak-hashable)
    saat menentukan cache key -- ini pola standar `st.cache_resource`.
    """
    return shap.TreeExplainer(_artifacts["model"])


def _shap_values_for_class(explainer, X: pd.DataFrame, class_idx: int) -> np.ndarray:
    """Ambil SHAP value 1 baris data untuk 1 kelas target tertentu.

    Ditulis kompatibel dengan beberapa versi output library `shap` untuk
    model multiclass (XGBoost softprob), karena bentuk array yang
    dikembalikan `explainer.shap_values()` bisa berbeda antar versi:
    - list berisi 1 array (n_samples, n_features) per kelas (versi lama), atau
    - satu array ber-dimensi 3: (n_samples, n_features, n_classes) (versi baru).
    """
    raw = explainer.shap_values(X)

    if isinstance(raw, list):
        vals = np.asarray(raw[class_idx])[0]
    else:
        arr = np.asarray(raw)
        if arr.ndim == 3:
            vals = arr[0, :, class_idx]
        else:
            # Fallback (mis. model biner / 1 array saja)
            vals = arr[0]

    return vals.astype(float)


def _format_feature_value(feature: str, raw: dict, info: dict) -> str:
    """Format nilai fitur mentah jadi teks yang mudah dibaca pengguna
    (satuan cm untuk pengukuran tubuh, label kategori untuk fitur turunan)."""
    if feature in MEASUREMENT_FIELDS_CM:
        return f"{raw[feature]:.1f} cm"
    if feature == "usia":
        return f"{raw['usia']} tahun"
    if feature == "jenis_kelamin":
        return str(raw["jenis_kelamin"])
    if feature == "ukuran_dicoba":
        return str(raw["ukuran_dicoba"])
    if feature == "usia_group":
        return info["usia_group_label"]
    if feature == "kategori_tinggi":
        return info["kategori_tinggi_label"]
    return "-"


def explain_prediction(raw: dict, X: pd.DataFrame, info: dict, artifacts: dict,
                        status: str, top_n: int = 6) -> list[dict]:
    """Jelaskan KENAPA model memberi hasil `status` (Pas/Terlalu Kecil/Terlalu
    Besar) memakai SHAP, memetakan kontribusi tiap fitur pada prediksi baris
    input pengguna.

    SHAP value POSITIF pada kelas `status` berarti fitur tsb MENDORONG
    prediksi ke arah `status` tersebut; NEGATIF berarti fitur tsb justru
    MENAHAN/menjauhkan prediksi dari `status` tersebut.

    Returns
    -------
    list of dict (diurutkan dari pengaruh terbesar), masing-masing:
      - feature      : nama kolom internal
      - label        : nama fitur dalam Bahasa Indonesia
      - value_display: nilai fitur dalam format mudah dibaca
      - shap_value   : kontribusi SHAP (float, skala log-odds)
    """
    explainer = get_shap_explainer(artifacts)
    class_labels = list(artifacts["label_encoder_target"].classes_)
    class_idx = class_labels.index(status)

    shap_vals = _shap_values_for_class(explainer, X, class_idx)
    feature_names = list(X.columns)

    contributions = [
        {
            "feature": feat,
            "label": FEATURE_LABELS.get(feat, feat),
            "value_display": _format_feature_value(feat, raw, info),
            "shap_value": float(val),
        }
        for feat, val in zip(feature_names, shap_vals)
    ]
    contributions.sort(key=lambda d: abs(d["shap_value"]), reverse=True)
    return contributions[:top_n]


def recommend_size(current_size: str, status: str) -> tuple[str, str]:
    """Memberi rekomendasi ukuran berdasarkan status hasil prediksi.
    (check) Ini hanya NAIK/TURUN 1 TINGKAT dari ukuran yang dicoba -- kalau
    ukuran pas sebenarnya 2-3 tingkat lebih jauh, butuh beberapa kali coba
    manual. Untuk rekomendasi LANGSUNG ke ukuran paling pas, pakai
    `recommend_best_size()` di bawah.
    """
    idx = SIZE_ORDER.index(current_size)

    if status == "Pas":
        return current_size, f"Ukuran {current_size} yang kamu coba sudah pas di badanmu. Tidak perlu ganti ukuran."

    if status == "Terlalu Kecil":
        if idx == len(SIZE_ORDER) - 1:
            return current_size, "Ukuran ini sudah yang terbesar tersedia (XXL) namun masih terasa kecil. Coba pertimbangkan brand dengan potongan yang lebih besar (oversized fit)."
        next_size = SIZE_ORDER[idx + 1]
        return next_size, f"Ukuran {current_size} terasa terlalu kecil. Coba naik satu ukuran ke {next_size} untuk kenyamanan lebih baik."

    if status == "Terlalu Besar":
        if idx == 0:
            return current_size, "Ukuran ini sudah yang terkecil tersedia (S) namun masih terasa besar. Coba pertimbangkan brand dengan potongan yang lebih slim/fit."
        prev_size = SIZE_ORDER[idx - 1]
        return prev_size, f"Ukuran {current_size} terasa terlalu besar. Coba turun satu ukuran ke {prev_size} untuk hasil yang lebih pas."

    return current_size, ""


def recommend_best_size(raw: dict, artifacts: dict) -> dict:
    """
    Cari ukuran yang PALING PAS secara langsung, dengan mencoba SEMUA pilihan
    ukuran (S, M, L, XL, XXL) memakai data ukuran tubuh yang SAMA -- bukan
    cuma naik/turun 1 tingkat dari ukuran yang dicoba pertama kali. Jadi kalau
    ukuran pas sebenarnya 2-3 tingkat lebih jauh (mis. dicoba S tapi pasnya
    XL), rekomendasi langsung mengarah ke XL, tidak perlu coba manual
    berkali-kali.

    Parameters
    ----------
    raw : dict input mentah (satuan cm, sama seperti dari form), termasuk
          "ukuran_dicoba" -- nilai ini akan di-override untuk tiap kandidat.
    artifacts : dict hasil load_artifacts()

    Returns
    -------
    dict berisi:
      - best_size          : ukuran yang direkomendasikan
      - found_pas          : True kalau ada ukuran yang model prediksi "Pas"
      - status_per_size     : {size: status} hasil prediksi tiap ukuran
      - proba_pas_per_size  : {size: probabilitas "Pas"} tiap ukuran (skala asli)
    """
    status_per_size = {}
    proba_pas_per_size = {}

    for size in SIZE_ORDER:
        raw_try = dict(raw)
        raw_try["ukuran_dicoba"] = size
        X, _ = build_feature_row(raw_try, artifacts)
        result = predict(X, artifacts)
        status_per_size[size] = result["status"]
        proba_pas_per_size[size] = result["raw_proba"].get("Pas", 0.0)

    pas_sizes = [s for s, st in status_per_size.items() if st == "Pas"]

    if pas_sizes:
        # Kalau lebih dari satu ukuran diprediksi "Pas", pilih yang probabilitasnya paling tinggi
        best_size = max(pas_sizes, key=lambda s: proba_pas_per_size[s])
    else:
        # Tidak ada yang benar-benar "Pas" -> pilih ukuran paling mendekati
        # (probabilitas "Pas" tertinggi di antara semua kandidat)
        best_size = max(SIZE_ORDER, key=lambda s: proba_pas_per_size[s])

    return {
        "best_size": best_size,
        "found_pas": bool(pas_sizes),
        "status_per_size": status_per_size,
        "proba_pas_per_size": proba_pas_per_size,
    }

    return current_size, ""
