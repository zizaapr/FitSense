# 👕 FitSense — Prediksi Ukuran Pakaian

Aplikasi Streamlit untuk memprediksi kecocokan ukuran pakaian (Pas / Terlalu Kecil /
Terlalu Besar) berdasarkan pengukuran tubuh, menggunakan model **XGBoost** yang sudah
dilatih sebelumnya (`model/xgboost_model.pkl`).

## 📁 Struktur Proyek

```
FitSense/
├── app.py                     # entry point Streamlit
├── requirements.txt
├── utils/
│   ├── style.py                # tema & CSS kustom
│   ├── avatars.py               # generator avatar SVG (6 variasi)
│   └── preprocessing.py         # load model, feature engineering, prediksi
├── pages_content/
│   ├── beranda.py                # halaman Beranda
│   ├── prediksi.py                # halaman Prediksi Ukuran
│   └── info_model.py              # halaman Informasi Model
└── model/                       # artefak hasil training (tidak diubah)
    ├── xgboost_model.pkl
    ├── feature_names.pkl
    ├── feature_encoders.pkl
    ├── label_encoder_target.pkl
    ├── kategori_bins.pkl
    ├── best_params.pkl
    └── confusion_matrix.npy
```

## 🚀 Cara Menjalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

Aplikasi akan terbuka otomatis di browser pada `http://localhost:8501`.

## ⚠️ Catatan Penting

1. **Pipeline model tidak diubah.** Seluruh proses feature engineering (pengelompokan
   usia → `usia_group`, pengelompokan tinggi badan → `kategori_tinggi`, encoding
   `ukuran_dicoba`) mengikuti persis artefak (`kategori_bins.pkl`,
   `feature_encoders.pkl`) yang dihasilkan dari proses training asli.

2. **Asumsi encoding `jenis_kelamin`.** Kolom ini ada di `feature_names.pkl` namun
   encoder-nya tidak ditemukan di `feature_encoders.pkl`. Berdasarkan pola LabelEncoder
   pada kolom lain (terurut alfabetis), aplikasi ini mengasumsikan:
   `Laki-laki → 0`, `Perempuan → 1` (lihat `GENDER_MAP` di `utils/preprocessing.py`).
   Jika ternyata terbalik dari notebook training aslinya, cukup tukar nilainya di sana.

3. **Versi scikit-learn.** Encoder pada file `.pkl` dibuat dengan scikit-learn versi
   `1.7.2`. Jika environment Anda memakai versi berbeda, akan muncul
   `InconsistentVersionWarning` (biasanya tetap aman, tapi disarankan menyamakan versi
   bila memungkinkan).

4. **Feature importance** pada halaman *Informasi Model* diambil langsung dari
   `model.feature_importances_`, sehingga membutuhkan library `xgboost` terpasang saat
   aplikasi dijalankan.
