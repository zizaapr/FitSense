"""
ml_utils.py
============
Modul integrasi model machine learning untuk aplikasi FitSense.

PENTING: Modul ini TIDAK mengubah sedikit pun logika preprocessing, feature
engineering, encoding, scaling, maupun model XGBoost yang sudah dilatih pada
notebook `body.ipynb`. Semua fungsi di sini hanya MEREPLIKASI persis kode yang
ada pada notebook (sel Data Preparation & Feature Engineering) agar satu baris
data baru dari form Streamlit bisa melewati pipeline yang identik dengan yang
dipakai saat training, lalu memuat artefak (.pkl) hasil training apa adanya
untuk melakukan inferensi.

Urutan fitur, nama kolom, rumus, dan bin/threshold SEMUA diambil apa adanya
dari notebook:
    - usia_group  -> pd.cut(usia, bins=[0,5,10,15,20,30,100], labels=[0..5])
    - kategori_tinggi -> pd.qcut(tinggi_badan, q=4,
                                  labels=["Pendek","Sedang","Tinggi","Sangat Tinggi"])
      (encoding kategori_tinggi memakai LabelEncoder yang sama persis dengan
      hasil training -> feature_encoders["kategori_tinggi"].pkl)
"""

from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"

# Kandidat lokasi dataset mentah (sama seperti path relatif di notebook:
# "../dataset/body.csv"). Dipakai HANYA untuk menghitung ulang batas kuantil
# (qcut bins) kategori_tinggi persis seperti proses training -- bukan untuk
# melatih ulang model.
DATASET_CANDIDATES = [
    BASE_DIR / "dataset" / "body.csv",
    BASE_DIR.parent / "dataset" / "body.csv",
    BASE_DIR / "body.csv",
]

# Urutan fitur PERSIS seperti feature_names.pkl hasil training
FEATURE_ORDER = [
    "jenis_kelamin", "usia", "lingkar_kepala", "lebar_bahu", "lebar_dada",
    "lingkar_perut", "lingkar_pinggang", "lingkar_pinggul", "panjang_lengan",
    "bahu_ke_pinggang", "pinggang_ke_lutut", "panjang_kaki", "tinggi_badan",
    "usia_group", "kategori_tinggi",
]

# Label & satuan untuk tiap fitur mentah yang diminta ke pengguna (form input)
RAW_FEATURE_META = {
    "jenis_kelamin":    {"label": "Jenis Kelamin", "unit": None,  "kind": "gender"},
    "usia":             {"label": "Usia",          "unit": "tahun", "kind": "number", "min": 0, "max": 100, "default": 22, "step": 1},
    "lingkar_kepala":   {"label": "Lingkar Kepala", "unit": "cm", "kind": "number", "min": 10, "max": 40, "default": 21, "step": 1},
    "lebar_bahu":       {"label": "Lebar Bahu",     "unit": "cm", "kind": "number", "min": 5,  "max": 40, "default": 14, "step": 1},
    "lebar_dada":       {"label": "Lebar Dada",     "unit": "cm", "kind": "number", "min": 5,  "max": 40, "default": 14, "step": 1},
    "lingkar_perut":    {"label": "Lingkar Perut",  "unit": "cm", "kind": "number", "min": 5,  "max": 60, "default": 20, "step": 1},
    "lingkar_pinggang": {"label": "Lingkar Pinggang", "unit": "cm", "kind": "number", "min": 5, "max": 60, "default": 19, "step": 1},
    "lingkar_pinggul":  {"label": "Lingkar Pinggul", "unit": "cm", "kind": "number", "min": 5, "max": 60, "default": 19, "step": 1},
    "panjang_lengan":   {"label": "Panjang Lengan", "unit": "cm", "kind": "number", "min": 5,  "max": 40, "default": 19, "step": 1},
    "bahu_ke_pinggang": {"label": "Bahu ke Pinggang", "unit": "cm", "kind": "number", "min": 5, "max": 40, "default": 18, "step": 1},
    "pinggang_ke_lutut":{"label": "Pinggang ke Lutut", "unit": "cm", "kind": "number", "min": 5, "max": 40, "default": 17, "step": 1},
    "panjang_kaki":     {"label": "Panjang Kaki",   "unit": "cm", "kind": "number", "min": 10, "max": 60, "default": 27, "step": 1},
    "tinggi_badan":     {"label": "Tinggi Badan",   "unit": "cm", "kind": "number", "min": 30, "max": 200, "default": 48, "step": 1},
}

USIA_BINS = [0, 5, 10, 15, 20, 30, 100]
USIA_LABELS = [0, 1, 2, 3, 4, 5]
USIA_GROUP_NAMES = {
    0: "Balita (0–5 th)",
    1: "Anak-anak (6–10 th)",
    2: "Pra-remaja (11–15 th)",
    3: "Remaja (16–20 th)",
    4: "Dewasa Muda (21–30 th)",
    5: "Dewasa (31+ th)",
}

GENDER_OPTIONS = {"Laki-laki": 1, "Perempuan": 2}

STATUS_META = {
    "Pas":            {"color": "#1E9E63", "bg": "#E7F8EF", "desc": "Ukuran pakaian sesuai dengan karakteristik tubuh Anda."},
    "Terlalu Besar":  {"color": "#D97706", "bg": "#FEF3E2", "desc": "Ukuran pakaian cenderung lebih besar dari yang dibutuhkan."},
    "Terlalu Kecil":  {"color": "#DC3452", "bg": "#FDECEF", "desc": "Ukuran pakaian cenderung lebih kecil dari yang dibutuhkan."},
}

# ---------------------------------------------------------------------------
# Nilai hasil evaluasi training YANG SEBENARNYA, sebagaimana tercetak pada
# notebook body.ipynb (sel "EVALUASI MODEL"). Nilai-nilai ini tidak dapat
# dihitung ulang secara live karena X_test/y_test asli tidak disertakan
# sebagai artefak deployment (hanya model & confusion_matrix.npy yang
# disimpan). Precision/Recall/F1 per-kelas & akurasi di bawah tetap dihitung
# ULANG secara live dari confusion_matrix.npy asli (lihat compute_metrics_from_cm),
# sedangkan AUC (butuh predict_proba pada seluruh X_test) diambil apa adanya
# dari output notebook karena tidak bisa direkonstruksi dari confusion matrix.
TRAINING_AUC_MACRO = 0.9450

DATASET_INFO_FALLBACK = {
    "total_raw": 716,
    "duplicates": 17,
    "total_clean": 699,
    "class_counts": {"Pas": 378, "Terlalu Kecil": 189, "Terlalu Besar": 132},
    "train_size": 559,
    "test_size": 140,
    "train_class_counts": {"Pas": 302, "Terlalu Kecil": 151, "Terlalu Besar": 106},
    "test_class_counts": {"Pas": 76, "Terlalu Kecil": 38, "Terlalu Besar": 26},
    "smote_size_per_class": 257,
}


@dataclass
class Artifacts:
    model: object
    scaler: object
    le_target: object
    feature_encoders: dict
    feature_names: list
    best_params: dict
    confusion_matrix: np.ndarray


@st.cache_resource(show_spinner=False)
def load_artifacts() -> Artifacts:
    """Memuat seluruh artefak hasil training apa adanya (tidak diubah)."""
    model = joblib.load(MODEL_DIR / "xgboost_model.pkl")
    scaler = joblib.load(MODEL_DIR / "scaler.pkl")
    le_target = joblib.load(MODEL_DIR / "label_encoder_target.pkl")
    feature_encoders = joblib.load(MODEL_DIR / "feature_encoders.pkl")
    feature_names = joblib.load(MODEL_DIR / "feature_names.pkl")
    best_params = joblib.load(MODEL_DIR / "best_params.pkl")
    cm = np.load(MODEL_DIR / "confusion_matrix.npy")
    return Artifacts(model, scaler, le_target, feature_encoders, feature_names, best_params, cm)


@st.cache_data(show_spinner=False)
def load_height_qcut_bins():
    """
    Menghitung ulang batas qcut untuk 'kategori_tinggi' dengan cara PERSIS
    seperti pada notebook (pd.qcut q=4 pada kolom tinggi_badan setelah
    cleaning & drop_duplicates). Jika dataset mentah tidak ditemukan di
    lokasi yang diharapkan, dipakai pendekatan kuantil normal dari
    mean/std scaler (statistik asli hasil training) sebagai fallback agar
    aplikasi tetap dapat berjalan.
    Return: (bin_edges: np.ndarray, is_from_real_dataset: bool)
    """
    for path in DATASET_CANDIDATES:
        if path.exists():
            try:
                raw = pd.read_csv(path)
                raw.columns = [c.strip() for c in raw.columns]
                raw = raw.rename(columns={"TotalHeight": "tinggi_badan"})
                raw = raw.drop_duplicates().reset_index(drop=True)
                _, bins = pd.qcut(
                    raw["tinggi_badan"], q=4,
                    labels=["Pendek", "Sedang", "Tinggi", "Sangat Tinggi"],
                    retbins=True,
                )
                bins = bins.copy()
                bins[0], bins[-1] = -np.inf, np.inf
                return bins, True
            except Exception:
                continue

    # Fallback: pendekatan kuantil normal memakai mean/std ASLI dari scaler
    # (scaler.pkl) hasil training untuk kolom tinggi_badan (index ke-12).
    # Catatan: hanya scaler.pkl & feature_names.pkl yang dimuat di sini (bukan
    # load_artifacts() penuh) agar tidak bergantung pada xgboost hanya untuk
    # menghitung fallback bin.
    from scipy.stats import norm
    scaler = joblib.load(MODEL_DIR / "scaler.pkl")
    feat_names = joblib.load(MODEL_DIR / "feature_names.pkl")
    idx = feat_names.index("tinggi_badan")
    mean = scaler.mean_[idx]
    std = scaler.scale_[idx]
    q1 = mean + std * norm.ppf(0.25)
    q2 = mean + std * norm.ppf(0.50)
    q3 = mean + std * norm.ppf(0.75)
    bins = np.array([-np.inf, q1, q2, q3, np.inf])
    return bins, False


def compute_usia_group(usia: float) -> int:
    """Replikasi persis: pd.cut(usia, bins=USIA_BINS, labels=USIA_LABELS)"""
    val = pd.cut([usia], bins=USIA_BINS, labels=USIA_LABELS)
    return int(val[0])


def compute_kategori_tinggi(tinggi_badan: float, bins: np.ndarray) -> str:
    """Replikasi persis: pd.qcut(tinggi_badan, q=4, labels=[...])"""
    labels = ["Pendek", "Sedang", "Tinggi", "Sangat Tinggi"]
    val = pd.cut([tinggi_badan], bins=bins, labels=labels)
    return str(val[0])


def build_feature_vector(raw_inputs: dict, artifacts: Artifacts, height_bins: np.ndarray) -> pd.DataFrame:
    """
    Membangun satu baris DataFrame fitur dengan urutan kolom PERSIS sama
    dengan feature_names.pkl, menerapkan feature engineering yang identik
    dengan notebook, lalu meng-encode kategori_tinggi memakai LabelEncoder
    ASLI hasil training (feature_encoders.pkl) -- bukan mapping buatan.
    """
    row = dict(raw_inputs)
    row["usia_group"] = compute_usia_group(raw_inputs["usia"])
    kategori_tinggi_label = compute_kategori_tinggi(raw_inputs["tinggi_badan"], height_bins)

    le_kategori_tinggi = artifacts.feature_encoders["kategori_tinggi"]
    row["kategori_tinggi"] = int(le_kategori_tinggi.transform([kategori_tinggi_label])[0])

    df = pd.DataFrame([row])[artifacts.feature_names]
    return df, kategori_tinggi_label


def predict(raw_inputs: dict):
    """
    Pipeline inferensi end-to-end: feature engineering -> scaling (scaler
    asli) -> prediksi model XGBoost asli -> decode label asli.
    """
    artifacts = load_artifacts()
    height_bins, from_real_dataset = load_height_qcut_bins()

    X_df, kategori_tinggi_label = build_feature_vector(raw_inputs, artifacts, height_bins)
    X_scaled = artifacts.scaler.transform(X_df.values)

    pred_encoded = artifacts.model.predict(X_scaled)[0]
    pred_proba = artifacts.model.predict_proba(X_scaled)[0]
    pred_label = artifacts.le_target.inverse_transform([pred_encoded])[0]

    proba_dict = {
        cls: float(pred_proba[i]) for i, cls in enumerate(artifacts.le_target.classes_)
    }

    usia_group_val = int(X_df["usia_group"].iloc[0])

    return {
        "label": pred_label,
        "confidence": float(pred_proba.max()),
        "proba": proba_dict,
        "usia_group": usia_group_val,
        "usia_group_name": USIA_GROUP_NAMES.get(usia_group_val, "-"),
        "kategori_tinggi": kategori_tinggi_label,
        "height_bins_from_real_dataset": from_real_dataset,
        "raw_inputs": raw_inputs,
    }


def compute_metrics_from_cm(cm: np.ndarray, class_names: list) -> dict:
    """
    Menghitung akurasi, precision/recall/f1 per kelas & weighted-average
    LANGSUNG dari confusion_matrix.npy asli hasil training (bukan angka
    hardcode). cm[i][j] = jumlah data kelas asli i diprediksi sebagai j.
    """
    cm = np.array(cm, dtype=float)
    n_classes = cm.shape[0]
    support = cm.sum(axis=1)
    total = cm.sum()

    accuracy = np.trace(cm) / total

    precisions, recalls, f1s = [], [], []
    for i in range(n_classes):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)

    weights = support / total
    weighted_precision = float(np.sum(np.array(precisions) * weights))
    weighted_recall = float(np.sum(np.array(recalls) * weights))
    weighted_f1 = float(np.sum(np.array(f1s) * weights))

    per_class = {
        class_names[i]: {
            "precision": precisions[i],
            "recall": recalls[i],
            "f1": f1s[i],
            "support": int(support[i]),
        }
        for i in range(n_classes)
    }

    return {
        "accuracy": float(accuracy),
        "precision_weighted": weighted_precision,
        "recall_weighted": weighted_recall,
        "f1_weighted": weighted_f1,
        "per_class": per_class,
        "support_total": int(total),
    }


def get_feature_importance(artifacts: Artifacts) -> pd.DataFrame:
    """Feature importance LANGSUNG dari model.feature_importances_ (bukan dummy)."""
    df = pd.DataFrame({
        "feature": artifacts.feature_names,
        "importance": artifacts.model.feature_importances_,
    }).sort_values("importance", ascending=False).reset_index(drop=True)
    return df


@st.cache_data(show_spinner=False)
def get_dataset_stats() -> dict:
    """
    Mengambil statistik dataset. Jika file dataset mentah (body.csv) ditemukan
    di lokasi yang diharapkan, statistik dihitung LIVE dengan replikasi persis
    langkah cleaning pada notebook (rename, isi missing modus, drop_duplicates,
    buat kolom target kesesuaian_ukuran). Jika tidak ditemukan, dipakai nilai
    dokumentasi hasil run notebook (bukan angka rekaan/dummy, melainkan
    output nyata dari proses training yang sudah dijalankan) sebagai fallback.
    """
    for path in DATASET_CANDIDATES:
        if path.exists():
            try:
                raw = pd.read_csv(path)
                raw.columns = [c.strip() for c in raw.columns]
                raw = raw.rename(columns={
                    "Gender": "jenis_kelamin", "Age": "usia",
                    "HeadCircumference": "lingkar_kepala", "ShoulderWidth": "lebar_bahu",
                    "ChestWidth": "lebar_dada", "Belly": "lingkar_perut",
                    "Waist": "lingkar_pinggang", "Hips": "lingkar_pinggul",
                    "ArmLength": "panjang_lengan", "ShoulderToWaist": "bahu_ke_pinggang",
                    "WaistToKnee": "pinggang_ke_lutut", "LegLength": "panjang_kaki",
                    "TotalHeight": "tinggi_badan",
                })
                total_raw = len(raw)
                if raw["jenis_kelamin"].isnull().sum() > 0:
                    modus = raw["jenis_kelamin"].mode()[0]
                    raw["jenis_kelamin"] = raw["jenis_kelamin"].fillna(modus)
                raw["jenis_kelamin"] = raw["jenis_kelamin"].astype(int)

                clean = raw.drop_duplicates().reset_index(drop=True)
                duplicates = total_raw - len(clean)

                circ_feats = ["lingkar_kepala", "lebar_bahu", "lebar_dada", "lingkar_perut",
                              "lingkar_pinggang", "lingkar_pinggul", "panjang_lengan",
                              "bahu_ke_pinggang", "pinggang_ke_lutut", "panjang_kaki"]
                clean["body_size_index"] = clean[circ_feats].sum(axis=1) / clean["tinggi_badan"]
                clean["usia_group_bantu"] = pd.cut(clean["usia"], bins=[0, 5, 10, 15, 20, 30, 100], labels=False)
                grp = clean.groupby(["usia_group_bantu", "jenis_kelamin"])["body_size_index"]
                grp_mean = grp.transform("mean")
                grp_std = grp.transform("std").replace(0, np.nan)
                clean["z"] = ((clean["body_size_index"] - grp_mean) / grp_std).fillna(0)
                threshold = 0.6
                kondisi = [clean["z"] > threshold, clean["z"] < -threshold]
                pilihan = ["Terlalu Besar", "Terlalu Kecil"]
                clean["kesesuaian_ukuran"] = np.select(kondisi, pilihan, default="Pas")

                class_counts = clean["kesesuaian_ukuran"].value_counts().to_dict()
                return {
                    "total_raw": total_raw,
                    "duplicates": duplicates,
                    "total_clean": len(clean),
                    "class_counts": class_counts,
                    "train_size": DATASET_INFO_FALLBACK["train_size"],
                    "test_size": DATASET_INFO_FALLBACK["test_size"],
                    "train_class_counts": DATASET_INFO_FALLBACK["train_class_counts"],
                    "test_class_counts": DATASET_INFO_FALLBACK["test_class_counts"],
                    "smote_size_per_class": DATASET_INFO_FALLBACK["smote_size_per_class"],
                    "source": "live",
                }
            except Exception:
                continue
    result = dict(DATASET_INFO_FALLBACK)
    result["source"] = "notebook"
    return result


FEATURE_DISPLAY_NAMES = {
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
    "usia_group": "Kelompok Usia",
    "kategori_tinggi": "Kategori Tinggi",
}
