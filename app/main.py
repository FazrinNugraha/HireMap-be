from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    SalaryEvaluationRequest,
    SalaryEvaluationResponse,
    SalaryPredictionRequest,
    SalaryPredictionResponse,
)
from app.services.constants import (
    CATEGORIES,
    CERTIFICATION_LEVELS,
    EDUCATION_LEVELS,
    EXPERIENCE_LEVELS,
    LOCATIONS,
)
from app.services.salary_service import predict_salary
from app.services.salary_zone_service import evaluate_salary
from app.services.spatial_service import get_industry_distribution, get_spatial_summary


app = FastAPI(
    title="HireMap API",
    version="0.1.0",
    description="FastAPI backend untuk model prediksi gaji, kos, dan data spasial HireMap.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _option_list(options: dict, multiplier_key: str) -> list[dict]:
    return [
        {"value": key, "label": value["label"], "multiplier": value[multiplier_key]}
        for key, value in options.items()
    ]


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok", "service": "hiremap-api"}


@app.get("/api/metadata")
def metadata() -> dict:
    return {
        "locations": LOCATIONS,
        "categories": CATEGORIES,
        "experience_levels": _option_list(EXPERIENCE_LEVELS, "m_pengalaman"),
        "education_levels": _option_list(EDUCATION_LEVELS, "m_pendidikan"),
        "certification_levels": _option_list(CERTIFICATION_LEVELS, "m_sertifikat"),
    }


@app.post("/api/salary/predict", response_model=SalaryPredictionResponse)
def predict_salary_endpoint(payload: SalaryPredictionRequest) -> dict:
    try:
        return predict_salary(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gagal melakukan prediksi: {exc}") from exc


@app.post("/api/salary/evaluate", response_model=SalaryEvaluationResponse)
def evaluate_salary_endpoint(payload: SalaryEvaluationRequest) -> dict:
    return evaluate_salary(payload.input_salary, payload.prediction.model_dump())


@app.get("/api/spatial/summary")
def spatial_summary() -> list[dict]:
    return get_spatial_summary()


@app.get("/api/spatial/industry-distribution")
def industry_distribution(category: str = Query(...)) -> list[dict]:
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Kategori pekerjaan tidak tersedia.")
    return get_industry_distribution(category)


