import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from icons import svg_icon
from utils.style import STATUS_COLORS, BRASS, BRASS_DARK, MUTED, PAS, BESAR, INK

DATASET_RAW_ROWS = 716
DATASET_CLEAN_ROWS = 699
DATASET_N_FEATURES = 16

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

HYPERPARAM_LABELS = {
    "n_estimators": "Jumlah Pohon (n_estimators)",
    "max_depth": "Kedalaman Maksimum Pohon (max_depth)",
    "learning_rate": "Learning Rate",
    "subsample": "Subsample Ratio",
    "colsample_bytree": "Colsample by Tree",
    "min_child_weight": "Min Child Weight",
    "gamma": "Gamma (Regularisasi Split)",
    "reg_alpha": "Reg Alpha (L1)",
    "reg_lambda": "Reg Lambda (L2)",
}

def _icon(name: str) -> str:
    icons = {
        "algo": """<rect x="7" y="7" width="10" height="10" rx="1.6" stroke-width="1.7"/>
            <path d="M9.5 3.6v3.1M14.5 3.6v3.1M9.5 17.3v3.1M14.5 17.3v3.1
                     M3.6 9.5h3.1M3.6 14.5h3.1M17.3 9.5h3.1M17.3 14.5h3.1" stroke-width="1.6" stroke-linecap="round"/>""",
        "database": """<ellipse cx="12" cy="5.5" rx="7.5" ry="2.6" stroke-width="1.7"/>
            <path d="M4.5 5.5v6.4c0 1.44 3.36 2.6 7.5 2.6s7.5-1.16 7.5-2.6V5.5" stroke-width="1.7"/>
            <path d="M4.5 11.9v6.4c0 1.44 3.36 2.6 7.5 2.6s7.5-1.16 7.5-2.6v-6.4" stroke-width="1.7"/>""",
        "target": """<circle cx="12" cy="12" r="8.4" stroke-width="1.7"/>
            <circle cx="12" cy="12" r="4.6" stroke-width="1.7"/>
            <circle cx="12" cy="12" r="1.1" fill="currentColor" stroke-width="0"/>""",
        "spark": """<path d="M12 3.5c.4 3.3 1.6 5.1 4.9 5.5-3.3.4-4.5 2.2-4.9 5.5-.4-3.3-1.6-5.1-4.9-5.5
                     3.3-.4 4.5-2.2 4.9-5.5z" stroke-width="1.5" stroke-linejoin="round"/>
            <path d="M18.5 14.2c.2 1.7.9 2.6 2.5 2.8-1.6.2-2.3 1.1-2.5 2.8-.2-1.7-.9-2.6-2.5-2.8
                     1.6-.2 2.3-1.1 2.5-2.8z" stroke-width="1.3" stroke-linejoin="round"/>""",
        "x-circle": """<circle cx="12" cy="12" r="8.4" stroke-width="1.7"/>
            <path d="m9.2 9.2 5.6 5.6M14.8 9.2l-5.6 5.6" stroke-width="1.7"/>""",
    }
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="#1B2A4A" stroke-linecap="round" stroke-linejoin="round">{icons[name]}</svg>'


def _clean(html: str) -> str:
    return "\n".join(line.strip() for line in html.strip().splitlines())


def _metrics_from_confusion_matrix(cm: np.ndarray, class_labels: list):
    rows = []
    total = cm.sum()
    for i, label in enumerate(class_labels):
        tp = cm[i, i]
        fn = cm[i, :].sum() - tp
        fp = cm[:, i].sum() - tp
        support = cm[i, :].sum()
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        rows.append({
            "Kelas": label, "Precision": precision, "Recall": recall,
            "F1-Score": f1, "Support": int(support),
        })
    df = pd.DataFrame(rows)
    accuracy = np.trace(cm) / total if total > 0 else 0.0
    w_precision = (df["Precision"] * df["Support"]).sum() / total if total > 0 else 0.0
    w_recall = (df["Recall"] * df["Support"]).sum() / total if total > 0 else 0.0
    w_f1 = (df["F1-Score"] * df["Support"]).sum() / total if total > 0 else 0.0
    weighted = {"precision": w_precision, "recall": w_recall, "f1": w_f1}
    return df, accuracy, weighted


def render(artifacts):
    model = artifacts["model"]
    best_params = artifacts["best_params"]
    cm = artifacts["confusion_matrix"]
    class_labels = list(artifacts["label_encoder_target"].classes_)
    feature_names = artifacts["feature_names"]

    metrics_df, accuracy, weighted = _metrics_from_confusion_matrix(cm, class_labels)

    st.markdown(
        _clean(
            f"""
            <div class="fs-card">
                <div class="fs-section-title">{svg_icon('layers', 19, '#1B2A4A')}&nbsp;Ringkasan Model</div>
                <div class="fs-model-grid">
                    <div class="fs-model-item">
                        <div class="fs-model-icon" style="background:#F4ECD8;">{_icon('algo')}</div>
                        <div>
                            <div class="fs-model-label">Algoritma</div>
                            <div class="fs-model-value">XGBoost</div>
                            <div class="fs-model-desc">Extreme Gradient Boosting Classifier</div>
                        </div>
                    </div>
                    <div class="fs-model-item">
                        <div class="fs-model-icon" style="background:#E9EBF3;">{_icon('database')}</div>
                        <div>
                            <div class="fs-model-label">Dataset</div>
                            <div class="fs-model-value">{DATASET_CLEAN_ROWS:,} data bersih</div>
                            <div class="fs-model-desc">Dari {DATASET_RAW_ROWS:,} data mentah pengukuran tubuh pengguna, {DATASET_N_FEATURES} fitur</div>
                        </div>
                    </div>
                    <div class="fs-model-item">
                        <div class="fs-model-icon" style="background:#F5E6E6;">{_icon('target')}</div>
                        <div>
                            <div class="fs-model-label">Target</div>
                            <div class="fs-model-value">Kesesuaian Ukuran</div>
                            <div class="fs-model-desc">3 kelas: {", ".join(class_labels)}</div>
                        </div>
                    </div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="fs-section-title">{svg_icon("gauge", 19, "#1B2A4A")}&nbsp;Performa Model</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"Dihitung langsung dari **{int(cm.sum()):,} data uji** (data yang tidak pernah dilihat model saat training).",
    )
    st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)

    metric_specs = [
        ("gauge", "Accuracy", accuracy, BRASS, "#F4ECD8"),
        ("target", "Precision (weighted)", weighted["precision"], BESAR, "#E7EEF3"),
        ("check-circle", "Recall (weighted)", weighted["recall"], PAS, "#E9F2EC"),
        ("trending-up", "F1-Score (weighted)", weighted["f1"], INK, "#E9EBF3"),
    ]
    metric_cards_html = "".join(
        f"""
        <div class="fs-metric-card">
            <div class="fs-metric-card-head">
                <div class="fs-metric-card-badge" style="background:{bg};">{svg_icon(name, 16, '#1B2A4A')}</div>
                <div class="fs-metric-card-label">{label}</div>
            </div>
            <div class="fs-metric-card-value">{value*100:.2f}%</div>
            <div class="fs-metric-card-track">
                <div class="fs-metric-card-fill" style="width:{value*100:.1f}%; background:{color};"></div>
            </div>
        </div>
        """
        for name, label, value, color, bg in metric_specs
    )
    st.markdown(
        _clean(f'<div class="fs-metric-grid fs-metric-grid-4">{metric_cards_html}</div>'),
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:0.9rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="fs-explain-box">
        <b>Precision</b> mengukur dari semua prediksi model untuk suatu kelas, berapa persen yang
        benar-benar tepat. <b>Recall</b> mengukur dari semua data yang sebenarnya berada di kelas
        tersebut, berapa persen yang berhasil dikenali model. <b>F1-Score</b> adalah rata-rata
        harmonik dari keduanya, dan <b>Support</b> adalah jumlah data uji pada kelas tersebut.
        Nilai <b>Precision/Recall/F1</b> di atas adalah rata-rata yang ditimbang
        (<i>weighted average</i>) sesuai jumlah data uji tiap kelas.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:1.1rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="fs-subheading">{svg_icon("bar-chart", 14, BRASS_DARK)}&nbsp;Rincian per Kelas</div>',
        unsafe_allow_html=True,
    )

    cards_html = ""
    for _, row in metrics_df.iterrows():
        color = STATUS_COLORS.get(row["Kelas"], BRASS)
        cards_html += f"""
            <div class="fs-class-card" style="--class-color:{color};">
                <div class="fs-class-card-head">
                    <span class="fs-class-card-name">
                        <span class="fs-shap-dot" style="background:{color};"></span>&nbsp;{row['Kelas']}
                    </span>
                    <span class="fs-class-card-f1">{row['F1-Score']*100:.1f}%</span>
                </div>
                <div class="fs-class-card-track">
                    <div class="fs-class-card-fill" style="width:{max(row['F1-Score']*100, 2):.1f}%;"></div>
                </div>
                <div class="fs-class-card-meta">
                    <span>Precision <b>{row['Precision']*100:.1f}%</b></span>
                    <span>Recall <b>{row['Recall']*100:.1f}%</b></span>
                    <span>Support <b>{row['Support']}</b></span>
                </div>
            </div>
        """
    st.markdown(f'<div class="fs-class-grid">{_clean(cards_html)}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="fs-section-title">{svg_icon("layers", 19, "#1B2A4A")}&nbsp;Feature Importance</div>',
        unsafe_allow_html=True,
    )

    importances = getattr(model, "feature_importances_", None)
    if importances is not None:
        fi_df = pd.DataFrame({
            "feature": feature_names,
            "importance": importances,
        })
        fi_df["label"] = fi_df["feature"].map(FEATURE_LABELS).fillna(fi_df["feature"])
        fi_df = fi_df.sort_values("importance", ascending=True)

        fig = go.Figure(go.Bar(
            x=fi_df["importance"], y=fi_df["label"], orientation="h",
            marker=dict(
                color=fi_df["importance"],
                colorscale=[[0, "#E9DFC2"], [0.55, "#A9821F"], [1, "#1B2A4A"]],
                line=dict(width=0),
            ),
            marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>Importance: %{x:.4f}<extra></extra>",
        ))
        fig.update_traces(marker_cornerradius=8)
        fig.update_layout(
            height=460, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Tingkat Kepentingan Fitur", yaxis_title="",
            font=dict(family="IBM Plex Mono, monospace", color="#1B2A4A", size=11),
            xaxis=dict(showgrid=True, gridcolor="#E3DBC6", zeroline=False),
            yaxis=dict(showgrid=False),
            bargap=0.28,
        )
        st.plotly_chart(fig, use_container_width=True)

        top3 = fi_df.sort_values("importance", ascending=False).head(3)["label"].tolist()
        if len(top3) == 1:
            top3_text = top3[0]
        elif len(top3) == 2:
            top3_text = f"{top3[0]} dan {top3[1]}"
        else:
            top3_text = f"{', '.join(top3[:-1])}, dan {top3[-1]}"

        st.markdown(
            f"""
            <div class="fs-explain-box">
            Grafik ini menunjukkan seberapa besar peran tiap fitur dalam keputusan model
            XGBoost secara keseluruhan (dihitung dari seberapa sering & seberapa efektif fitur
            tersebut dipakai untuk membelah data di semua pohon keputusan). Semakin panjang
            batang (dan semakin gelap warnanya), semakin besar pengaruh fitur tersebut terhadap
            hasil prediksi. Untuk model ini, tiga fitur paling berpengaruh adalah
            <b>{top3_text}</b> artinya perubahan pada ukuran-ukuran tersebut paling banyak
            menggeser prediksi model dibanding fitur lainnya.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning(
            "Tidak dapat mengambil feature_importances_ dari model saat ini. Pastikan library "
            "**xgboost** terpasang di environment yang menjalankan aplikasi ini."
        )
    st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="fs-section-title">{svg_icon("target", 19, "#1B2A4A")}&nbsp;Confusion Matrix</div>',
        unsafe_allow_html=True,
    )

    total_uji = int(cm.sum())
    total_benar = int(np.trace(cm))
    total_salah = total_uji - total_benar
    cm_stats = [
        ("check-circle", "Prediksi Benar", f"{total_benar:,}", PAS, "#E9F2EC"),
        ("x-circle", "Prediksi Salah", f"{total_salah:,}", "#B14D3D", "#F5E6E6"),
        ("layers", "Total Data Uji", f"{total_uji:,}", BRASS_DARK, "#F4ECD8"),
    ]
    cm_stats_html = "".join(
        f"""
        <div class="fs-cm-stat">
            <div class="fs-cm-stat-badge" style="background:{bg};">{_icon(icon) if icon == 'x-circle' else svg_icon(icon, 17, '#1B2A4A')}</div>
            <div>
                <div class="fs-cm-stat-label">{label}</div>
                <div class="fs-cm-stat-value">{value}</div>
            </div>
        </div>
        """
        for icon, label, value, color, bg in cm_stats
    )
    st.markdown(_clean(f'<div class="fs-cm-stats">{cm_stats_html}</div>'), unsafe_allow_html=True)

    fig_cm = px.imshow(
        cm, x=class_labels, y=class_labels, text_auto=True,
        color_continuous_scale=[[0, "#F6F2E7"], [0.5, "#C9A961"], [1, "#1B2A4A"]],
        labels=dict(x="Prediksi Model", y="Aktual (Sebenarnya)", color="Jumlah"),
    )
    fig_cm.update_traces(
        textfont=dict(family="IBM Plex Mono, monospace", size=14),
        xgap=4, ygap=4,
    )
    fig_cm.update_layout(
        height=420, margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Mono, monospace", color="#1B2A4A"),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_cm, use_container_width=True)

    st.markdown(
        """
        <div class="fs-explain-box">
        Confusion matrix menunjukkan perbandingan antara label <b>aktual</b> (baris) dan label
        <b>hasil prediksi model</b> (kolom) pada data uji. Nilai pada diagonal (kiri-atas ke
        kanan-bawah) menunjukkan jumlah prediksi yang <b>benar</b>, sedangkan nilai di luar
        diagonal menunjukkan jumlah kesalahan prediksi (model salah menebak kelas). Semakin
        besar angka pada diagonal dan semakin kecil angka di luar diagonal, semakin baik
        performa model dalam membedakan ketiga status kecocokan ukuran.
        </div>
        """,
        unsafe_allow_html=True,
    )
