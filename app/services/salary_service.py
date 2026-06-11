import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack

from app.core.model_loader import load_salary_resources
from app.services.constants import (
    CERTIFICATION_LEVELS,
    EDUCATION_LEVELS,
    EXPERIENCE_LEVELS,
    GENERIC_CATEGORY_KEYWORDS,
    GENERIC_TITLE_TERMS,
    NON_PRIME_LOCATIONS,
)
from app.services.housing_service import predict_kos_price


def tokenize_title(job_title: str) -> list[str]:
    cleaned = (
        job_title.lower()
        .replace("/", " ")
        .replace("-", " ")
        .replace(",", " ")
        .replace(".", " ")
    )
    return [token for token in cleaned.split() if token]


def analyze_title_ambiguity(job_title: str, category: str, location: str) -> dict:
    tokens = tokenize_title(job_title)
    token_count = len(tokens)
    generic_matches = [token for token in tokens if token in GENERIC_TITLE_TERMS]
    category_matches = [
        token for token in tokens if token in GENERIC_CATEGORY_KEYWORDS.get(category, set())
    ]

    is_single_generic = token_count == 1 and len(generic_matches) == 1
    is_short_generic = token_count <= 2 and len(generic_matches) >= 1
    is_ambiguous = is_single_generic or is_short_generic or (
        token_count <= 2 and len(category_matches) >= 1
    )

    title_correction = 1.0
    confidence_label = "Tinggi"

    if is_single_generic:
        title_correction *= 0.84
        confidence_label = "Rendah"
    elif is_short_generic:
        title_correction *= 0.90
        confidence_label = "Sedang"
    elif len(generic_matches) >= 1:
        title_correction *= 0.95
        confidence_label = "Sedang"

    if is_ambiguous and location in NON_PRIME_LOCATIONS:
        title_correction *= 0.97

    if is_ambiguous and category == "Administrative & Customer Service":
        title_correction *= 0.97

    notes = []
    if is_single_generic:
        notes.append("Judul pekerjaan sangat umum, sehingga sistem menerapkan koreksi realistis.")
    elif is_short_generic:
        notes.append("Judul masih cukup generik, sehingga estimasi dibuat lebih konservatif.")

    if is_ambiguous:
        notes.append(
            "Coba judul yang lebih spesifik seperti 'Admin Finance', 'HR Staff', atau 'Customer Service Staff' untuk akurasi yang lebih baik."
        )

    return {
        "is_ambiguous": is_ambiguous,
        "generic_matches": generic_matches,
        "title_correction": round(title_correction, 4),
        "confidence_label": confidence_label,
        "notes": notes,
    }


def get_profile_adjustment(
    experience_level: str,
    education_level: str,
    certification_level: str,
    category: str,
) -> dict:
    experience = EXPERIENCE_LEVELS[experience_level]
    education = EDUCATION_LEVELS[education_level]
    certification = CERTIFICATION_LEVELS[certification_level]

    m_peng = experience["m_pengalaman"]
    m_pend = education["m_pendidikan"]
    m_sert = certification["m_sertifikat"]

    realism_correction = 1.0
    notes = []

    if "Entry-Level" in experience_level:
        realism_correction *= 0.97
        notes.append("Entry-level diberi penyesuaian ekstra agar hasil lebih realistis.")

        if category in {
            "Administrative & Customer Service",
            "HR & General Affairs",
            "Retail, F&B & Hospitality",
        }:
            realism_correction *= 0.97
            notes.append("Role entry-level umum di kategori ini dibuat lebih konservatif.")

    elif "Junior" in experience_level and category in {
        "Administrative & Customer Service",
        "HR & General Affairs",
    }:
        realism_correction *= 0.98

    total_multiplier = m_peng * m_pend * m_sert * realism_correction
    return {
        "m_pengalaman": m_peng,
        "m_pendidikan": m_pend,
        "m_sertifikat": m_sert,
        "realism_correction": round(realism_correction, 4),
        "total_multiplier": round(total_multiplier, 4),
        "notes": notes,
        "labels": {
            "pengalaman": experience["label"],
            "pendidikan": education["label"],
            "sertifikasi": certification["label"],
        },
    }


def predict_base_salary(job_title: str, category: str, location: str) -> float:
    """Replicate the legacy Streamlit ML feature pipeline."""
    resources = load_salary_resources()
    model = resources["model"]
    tfidf_word = resources["tfidf_word"]
    tfidf_char = resources["tfidf_char"]
    ohe_encoder = resources["ohe_encoder"]

    x_word = tfidf_word.transform([job_title])
    x_char = tfidf_char.transform([job_title])

    title_len = len(job_title)
    title_wc = len(job_title.split())
    extra = csr_matrix([[title_len, title_wc, 0]])
    target_sparse = csr_matrix([[5000000]])

    df_cat = pd.DataFrame(
        {
            "Lokasi_Clean": [location],
            "Kategori_Pekerjaan": [category],
            "Senioritas": ["Mid-Level/Staff"],
        }
    )
    x_ohe_full = ohe_encoder.transform(df_cat)
    x_ohe = x_ohe_full[:, :-3]

    x_final = hstack([x_word, x_char, target_sparse, extra, x_ohe])
    pred_log = model.predict(x_final)[0]
    return float(np.expm1(pred_log))


def predict_salary(payload) -> dict:
    job_title = payload.job_title.strip()
    base_salary = predict_base_salary(job_title, payload.category, payload.location)

    title_meta = analyze_title_ambiguity(job_title, payload.category, payload.location)
    profile_meta = get_profile_adjustment(
        payload.experience_level,
        payload.education_level,
        payload.certification_level,
        payload.category,
    )

    title_correction = title_meta["title_correction"]
    total_multiplier = profile_meta["total_multiplier"]
    salary_after_title_correction = base_salary * title_correction
    final_salary = int(salary_after_title_correction * total_multiplier)

    estimated_kos = predict_kos_price(payload.location)
    kos_ratio = (estimated_kos / final_salary) * 100 if final_salary else 0

    return {
        "judul": job_title,
        "kategori": payload.category,
        "lokasi": payload.location,
        "pengalaman": profile_meta["labels"]["pengalaman"],
        "pendidikan": profile_meta["labels"]["pendidikan"],
        "sertifikasi": profile_meta["labels"]["sertifikasi"],
        "gaji_basis": int(base_salary),
        "gaji_setelah_koreksi_judul": int(salary_after_title_correction),
        "gaji_prediksi": final_salary,
        "gaji_min": int(final_salary * 0.90),
        "gaji_max": int(final_salary * 1.10),
        "multiplier": round(total_multiplier, 2),
        "m_pengalaman": profile_meta["m_pengalaman"],
        "m_pendidikan": profile_meta["m_pendidikan"],
        "m_sertifikat": profile_meta["m_sertifikat"],
        "m_koreksi_realistis": profile_meta["realism_correction"],
        "m_koreksi_judul": title_correction,
        "is_ambiguous_title": title_meta["is_ambiguous"],
        "generic_tokens": title_meta["generic_matches"],
        "confidence_label": title_meta["confidence_label"],
        "adjustment_notes": title_meta["notes"] + profile_meta["notes"],
        "estimasi_kos": estimated_kos,
        "rasio_kos": kos_ratio,
    }


