"""
utils.py
========
Semua logika non-visual FitSense: memuat artefak model (.pkl), rekayasa fitur
turunan (usia_group, kategori_tinggi), encoding, scaling, dan prediksi.

CATATAN PENTING / PERINGATAN TENTANG SATUAN DATA
--------------------------------------------------
File .pkl yang diberikan TIDAK menyertakan kode sumber notebook pelatihan,
dan setelah memeriksa isi scaler.pkl, statistik (mean & std) fitur numerik
TERNYATA TIDAK COCOK dengan satuan sentimeter orang dewasa yang wajar,
misalnya:
    - tinggi_badan     : mean = 48.3   (bukan ~150-175 seperti tinggi cm dewasa)
    - lingkar_kepala   : mean = 20.5   (bukan ~54-58 seperti lingkar kepala cm dewasa)
    - usia             : mean = 15.4, std = 11.3

Artinya satuan asli data latih KEMUNGKINAN BUKAN cm/tahun standar (bisa jadi
data disintesis/di-generate acak saat pembuatan dataset skripsi/tugas, atau
memakai satuan/skala lain yang tidak terdokumentasi). Karena tidak ada
dataset atau notebook asli yang menyertai file model ini, rentang input
(FIELD_RANGES) dan ambang batas (USIA_BINS, TINGGI_BINS) di bawah ini
DIREKONSTRUKSI dari statistik scaler.pkl (mean & std) yang tersimpan --
BUKAN dari definisi asli.

Jika Anda memiliki notebook / dataset pelatihan asli, mohon sesuaikan
FIELD_RANGES, USIA_BINS, TINGGI_BINS, dan GENDER_MAP di bawah ini agar
identik dengan proses feature engineering asli, supaya hasil prediksi
benar-benar konsisten dengan performa model yang dilaporkan.

Untuk `jenis_kelamin`, tidak ada encoder tersimpan (berarti di-encode manual
dengan dict, bukan LabelEncoder). Nilai rata-rata (mean) hasil scaler adalah
1.45 dari kemungkinan nilai {1, 2}, sehingga diasumsikan mapping:
    Perempuan -> 1, Laki-laki -> 2
Silakan sesuaikan `GENDER_MAP` di bawah bila mapping asli Anda berbeda.
"""

import os
import joblib
import numpy as np
import pandas as pd

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")

# ---------------------------------------------------------------------------
# ASUMSI YANG BISA DIEDIT (silakan sesuaikan dengan notebook training asli)
# ---------------------------------------------------------------------------
GENDER_MAP = {"Perempuan": 1, "Laki-laki": 2}

# --- DIREKONSTRUKSI dari mean/std scaler.pkl (lihat catatan di atas) ---
# usia: mean=15.43, std=11.29 -> 5 kelompok berbasis kuantil distribusi normal.
# Nama kelompok dibuat NETRAL (bukan label usia dunia-nyata seperti
# "remaja"/"dewasa") karena satuan asli "usia" pada dataset ini tidak dapat
# dipastikan (lihat catatan satuan data di atas modul ini).
USIA_BINS = [-999, 5.95, 12.6, 18.25, 24.9, 999]
USIA_LABELS = ["Kelompok Usia A (paling muda)", "Kelompok Usia B", "Kelompok Usia C",
               "Kelompok Usia D", "Kelompok Usia E (paling tua)"]
USIA_CODES = [0, 1, 2, 3, 4]

# tinggi_badan: mean=48.26, std=12.03 -> 4 kelompok kuantil.
# Nama kategori ('Pendek'/'Sedang'/'Tinggi'/'Sangat Tinggi') DIAMBIL LANGSUNG
# dari feature_encoders['kategori_tinggi'].classes_ (data asli & valid),
# hanya AMBANG BATAS angkanya yang direkonstruksi dari statistik scaler.
TINGGI_BINS = [-999, 40.1, 48.3, 56.4, 999]
TINGGI_LABELS = ["Pendek", "Sedang", "Tinggi", "Sangat Tinggi"]

# Rentang input untuk validasi UI. Nilai default = mean, min/max ~ mean ± 3*std
# dari scaler.pkl (dibulatkan). SATUAN TIDAK DIKETAHUI PASTI (lihat catatan di
# atas) -- silakan sesuaikan bila Anda mengetahui satuan/rentang asli dataset.
FIELD_RANGES = {
    "usia":              dict(label="Usia", unit="satuan dataset", min=1,  max=50, default=15),
    "tinggi_badan":      dict(label="Tinggi Badan", unit="satuan dataset", min=10, max=85, default=48),
    "lingkar_kepala":    dict(label="Lingkar Kepala", unit="satuan dataset", min=5,  max=33, default=21),
    "lebar_bahu":        dict(label="Lebar Bahu", unit="satuan dataset", min=1,  max=30, default=14),
    "lebar_dada":        dict(label="Lebar Dada", unit="satuan dataset", min=1,  max=31, default=15),
    "lingkar_perut":     dict(label="Lingkar Perut", unit="satuan dataset", min=1,  max=53, default=20),
    "lingkar_pinggang":  dict(label="Lingkar Pinggang", unit="satuan dataset", min=1,  max=47, default=19),
    "lingkar_pinggul":   dict(label="Lingkar Pinggul", unit="satuan dataset", min=1,  max=46, default=19),
    "panjang_lengan":    dict(label="Panjang Lengan", unit="satuan dataset", min=1,  max=36, default=19),
    "bahu_ke_pinggang":  dict(label="Bahu ke Pinggang", unit="satuan dataset", min=1,  max=34, default=18),
    "pinggang_ke_lutut": dict(label="Pinggang ke Lutut", unit="satuan dataset", min=1,  max=33, default=17),
    "panjang_kaki":      dict(label="Panjang Kaki", unit="satuan dataset", min=1,  max=51, default=27),
}

RAW_INPUT_ORDER = [
    "jenis_kelamin", "usia", "tinggi_badan", "lingkar_kepala", "lebar_bahu",
    "lebar_dada", "lingkar_perut", "lingkar_pinggang", "lingkar_pinggul",
    "panjang_lengan", "bahu_ke_pinggang", "pinggang_ke_lutut", "panjang_kaki",
]

HASIL_STYLE = {
    "Pas": dict(
        color="#16A34A", bg="#ECFDF5", border="#A7F3D0", icon="check-circle",
        judul="Ukuran Sudah Pas!",
        pesan="Berdasarkan karakteristik tubuh yang Anda masukkan, ukuran pakaian yang Anda pertimbangkan sudah sesuai dengan bentuk tubuh Anda."
    ),
    "Terlalu Besar": dict(
        color="#D97706", bg="#FFFBEB", border="#FDE68A", icon="arrow-down-circle",
        judul="Ukuran Terlalu Besar",
        pesan="Model memprediksi ukuran pakaian ini cenderung terlalu besar untuk bentuk tubuh Anda. Pertimbangkan memilih satu ukuran lebih kecil."
    ),
    "Terlalu Kecil": dict(
        color="#DC2626", bg="#FEF2F2", border="#FECACA", icon="arrow-up-circle",
        judul="Ukuran Terlalu Kecil",
        pesan="Model memprediksi ukuran pakaian ini cenderung terlalu kecil untuk bentuk tubuh Anda. Pertimbangkan memilih satu ukuran lebih besar."
    ),
}

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
    "usia_group": "Kelompok Usia",
    "kategori_tinggi": "Kategori Tinggi",
}


# ---------------------------------------------------------------------------
# Loading artefak (di-cache oleh Streamlit lewat wrapper di app.py)
# ---------------------------------------------------------------------------
def load_artifacts():
    """Memuat semua artefak model dari folder /model. Mengembalikan dict."""
    artifacts = {}
    artifacts["feature_names"] = joblib.load(os.path.join(MODEL_DIR, "feature_names.pkl"))
    artifacts["feature_encoders"] = joblib.load(os.path.join(MODEL_DIR, "feature_encoders.pkl"))
    artifacts["label_encoder_target"] = joblib.load(os.path.join(MODEL_DIR, "label_encoder_target.pkl"))
    artifacts["scaler"] = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
    artifacts["model"] = joblib.load(os.path.join(MODEL_DIR, "xgboost_model.pkl"))
    try:
        artifacts["best_params"] = joblib.load(os.path.join(MODEL_DIR, "best_params.pkl"))
    except Exception:
        artifacts["best_params"] = {}
    try:
        artifacts["confusion_matrix"] = np.load(os.path.join(MODEL_DIR, "confusion_matrix.npy"))
    except Exception:
        artifacts["confusion_matrix"] = None
    return artifacts


def bin_usia(usia: float) -> int:
    label = pd.cut([usia], bins=USIA_BINS, labels=USIA_CODES, right=False)[0]
    return int(label)


def bin_usia_label(usia: float) -> str:
    label = pd.cut([usia], bins=USIA_BINS, labels=USIA_LABELS, right=False)[0]
    return str(label)


def bin_tinggi_label(tinggi: float) -> str:
    label = pd.cut([tinggi], bins=TINGGI_BINS, labels=TINGGI_LABELS, right=False)[0]
    return str(label)


def build_feature_row(raw_input: dict, artifacts: dict) -> pd.DataFrame:
    """
    Mengubah input mentah dari form menjadi 1 baris DataFrame terskala,
    siap dipakai model.predict(), dengan urutan kolom identik feature_names.pkl.
    """
    feature_names = artifacts["feature_names"]
    encoders = artifacts["feature_encoders"]
    scaler = artifacts["scaler"]

    row = {}
    row["jenis_kelamin"] = GENDER_MAP[raw_input["jenis_kelamin"]]
    row["usia"] = raw_input["usia"]
    row["lingkar_kepala"] = raw_input["lingkar_kepala"]
    row["lebar_bahu"] = raw_input["lebar_bahu"]
    row["lebar_dada"] = raw_input["lebar_dada"]
    row["lingkar_perut"] = raw_input["lingkar_perut"]
    row["lingkar_pinggang"] = raw_input["lingkar_pinggang"]
    row["lingkar_pinggul"] = raw_input["lingkar_pinggul"]
    row["panjang_lengan"] = raw_input["panjang_lengan"]
    row["bahu_ke_pinggang"] = raw_input["bahu_ke_pinggang"]
    row["pinggang_ke_lutut"] = raw_input["pinggang_ke_lutut"]
    row["panjang_kaki"] = raw_input["panjang_kaki"]
    row["tinggi_badan"] = raw_input["tinggi_badan"]

    # fitur turunan
    row["usia_group"] = bin_usia(raw_input["usia"])
    kategori_tinggi_label = bin_tinggi_label(raw_input["tinggi_badan"])
    row["kategori_tinggi"] = int(encoders["kategori_tinggi"].transform([kategori_tinggi_label])[0])

    df = pd.DataFrame([row])[feature_names]
    scaled = scaler.transform(df)
    scaled_df = pd.DataFrame(scaled, columns=feature_names)
    return df, scaled_df


def predict(raw_input: dict, artifacts: dict):
    """Mengembalikan (label_hasil, dict_probabilitas_per_kelas, df_fitur_asli)."""
    raw_df, scaled_df = build_feature_row(raw_input, artifacts)
    model = artifacts["model"]
    label_encoder = artifacts["label_encoder_target"]

    pred_idx = model.predict(scaled_df)[0]
    label = label_encoder.inverse_transform([pred_idx])[0]

    proba = {}
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(scaled_df)[0]
        for cls_idx, p in enumerate(probs):
            cls_label = label_encoder.inverse_transform([cls_idx])[0]
            proba[cls_label] = float(p)

    return label, proba, raw_df


def get_feature_importance(artifacts: dict) -> pd.DataFrame:
    """Mengambil feature_importances_ langsung dari model XGBoost terlatih."""
    model = artifacts["model"]
    feature_names = artifacts["feature_names"]
    importances = getattr(model, "feature_importances_", None)
    if importances is None:
        return pd.DataFrame(columns=["fitur", "label", "importance"])
    df = pd.DataFrame({
        "fitur": feature_names,
        "importance": importances,
    })
    df["label"] = df["fitur"].map(FEATURE_LABELS).fillna(df["fitur"])
    df = df.sort_values("importance", ascending=False).reset_index(drop=True)
    return df


def compute_metrics_from_confusion(cm: np.ndarray, class_labels):
    """Menghitung accuracy, precision, recall, f1 (macro) dari confusion matrix asli."""
    if cm is None:
        return None
    total = cm.sum()
    acc = np.trace(cm) / total if total else 0
    precisions, recalls, f1s = [], [], []
    for i in range(cm.shape[0]):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
    return {
        "accuracy": acc,
        "precision": float(np.mean(precisions)),
        "recall": float(np.mean(recalls)),
        "f1": float(np.mean(f1s)),
        "n_samples": int(total),
    }
