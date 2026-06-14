from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    AiChatRequest,
    AiChatResponse,
    SalaryEvaluationRequest,
    SalaryEvaluationResponse,
    SalaryPredictionRequest,
    SalaryPredictionResponse,
)
from app.services.ai_service import chat_with_career_consultant
from app.services.constants import (
    CATEGORIES,
    CERTIFICATION_LEVELS,
    COORDINATES,
    EDUCATION_LEVELS,
    EXPERIENCE_LEVELS,
    LOCATIONS,
)
from app.services.salary_service import predict_salary
from app.services.salary_zone_service import evaluate_salary
from app.services.spatial_service import (
    get_industry_distribution,
    get_location_detail,
    get_spatial_summary,
)


app = FastAPI(
    title="HireMap API",
    version="0.1.0",
    description="FastAPI backend untuk model prediksi gaji, kos, data spasial, dan AI consultant HireMap.",
)

# CORS mengizinkan frontend Vite lokal mengakses API backend saat development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _option_list(options: dict, multiplier_key: str) -> list[dict]:
    """Ubah dictionary multiplier backend menjadi format dropdown frontend.

    Di constants.py, pilihan pengalaman/pendidikan/sertifikasi disimpan sebagai
    dictionary agar mudah dicari berdasarkan key. Frontend butuh bentuk list
    berisi value, label, dan multiplier supaya bisa langsung dirender sebagai
    dropdown serta ditampilkan sebagai metadata model.
    """
    return [
        {"value": key, "label": value["label"], "multiplier": value[multiplier_key]}
        for key, value in options.items()
    ]


@app.get("/api/health")
def health_check() -> dict:
    """Endpoint sederhana untuk memastikan API backend hidup."""
    return {"status": "ok", "service": "hiremap-api"}


@app.get("/api/metadata")
def metadata() -> dict:
    """Kirim opsi dropdown yang dibutuhkan form Salary Prediction.

    Frontend memanggil endpoint ini saat app dibuka. Selain list lokasi dan
    kategori, endpoint juga mengirim multiplier agar UI bisa menjelaskan faktor
    pengalaman, pendidikan, dan sertifikasi dengan data yang sama seperti model.
    """
    return {
        "locations": LOCATIONS,
        "categories": CATEGORIES,
        "experience_levels": _option_list(EXPERIENCE_LEVELS, "m_pengalaman"),
        "education_levels": _option_list(EDUCATION_LEVELS, "m_pendidikan"),
        "certification_levels": _option_list(CERTIFICATION_LEVELS, "m_sertifikat"),
    }


@app.post("/api/salary/predict", response_model=SalaryPredictionResponse)
def predict_salary_endpoint(payload: SalaryPredictionRequest) -> dict:
    """Endpoint utama untuk menghitung prediksi gaji.

    Validasi input dilakukan oleh SalaryPredictionRequest di schemas.py. Setelah
    valid, payload diteruskan ke service predict_salary yang menjalankan model,
    koreksi judul, multiplier profil, estimasi kos, dan rasio kos.
    """
    try:
        return predict_salary(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gagal melakukan prediksi: {exc}") from exc


@app.post("/api/salary/evaluate", response_model=SalaryEvaluationResponse)
def evaluate_salary_endpoint(payload: SalaryEvaluationRequest) -> dict:
    """Evaluasi salary user terhadap range prediksi yang sudah dihitung."""
    return evaluate_salary(payload.input_salary, payload.prediction.model_dump())


@app.post("/api/ai/chat", response_model=AiChatResponse)
def ai_chat_endpoint(payload: AiChatRequest) -> dict:
    """Endpoint chat AI Consultant.

    Endpoint ini menerima message terbaru, history percakapan, dan optional
    prediction_context. Service AI akan mengubah history ke format Gemini dan
    membangun system prompt berdasarkan konteks prediksi user.
    """
    try:
        reply = chat_with_career_consultant(
            message=payload.message,
            history=[message.model_dump() for message in payload.history],
            prediction_context=(
                payload.prediction_context.model_dump()
                if payload.prediction_context is not None
                else None
            ),
        )
        return {"reply": reply}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gagal memproses AI consultant: {exc}") from exc


@app.get("/api/spatial/summary")
def spatial_summary() -> list[dict]:
    """Ringkasan lowongan, kos, dan koordinat untuk Spatial Map."""
    return get_spatial_summary()


@app.get("/api/spatial/industry-distribution")
def industry_distribution(category: str = Query(...)) -> list[dict]:
    """Distribusi lowongan per kota untuk satu kategori pekerjaan."""
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Kategori pekerjaan tidak tersedia.")
    return get_industry_distribution(category)


@app.get("/api/spatial/location-detail")
def location_detail_endpoint(
    location: str = Query(...),
    category: str = Query(None),
) -> dict:
    """Detail satu lokasi untuk sidebar Spatial Map."""
    if location not in COORDINATES:
        raise HTTPException(status_code=400, detail="Lokasi tidak ditemukan.")
    return get_location_detail(location, category)
