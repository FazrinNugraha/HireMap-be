from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.services.constants import (
    CATEGORIES,
    CERTIFICATION_LEVELS,
    EDUCATION_LEVELS,
    EXPERIENCE_LEVELS,
    LOCATIONS,
)


class SalaryPredictionRequest(BaseModel):
    job_title: str = Field(..., min_length=1, examples=["Data Analyst"])
    category: str = Field(..., examples=["IT, Tech & Data"])
    location: str = Field(..., examples=["Jakarta Selatan"])
    experience_level: str = Field("💼 Mid-Level (3-5 thn)", examples=["💼 Mid-Level (3-5 thn)"])
    education_level: str = Field("🎓 S1 / Sarjana", examples=["🎓 S1 / Sarjana"])
    certification_level: str = Field("📄 Tanpa Sertifikasi", examples=["📄 Tanpa Sertifikasi"])

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        if value not in CATEGORIES:
            raise ValueError("Kategori pekerjaan tidak tersedia.")
        return value

    @field_validator("location")
    @classmethod
    def validate_location(cls, value: str) -> str:
        if value not in LOCATIONS:
            raise ValueError("Lokasi tidak tersedia.")
        return value

    @field_validator("experience_level")
    @classmethod
    def validate_experience_level(cls, value: str) -> str:
        if value not in EXPERIENCE_LEVELS:
            raise ValueError("Level pengalaman tidak tersedia.")
        return value

    @field_validator("education_level")
    @classmethod
    def validate_education_level(cls, value: str) -> str:
        if value not in EDUCATION_LEVELS:
            raise ValueError("Level pendidikan tidak tersedia.")
        return value

    @field_validator("certification_level")
    @classmethod
    def validate_certification_level(cls, value: str) -> str:
        if value not in CERTIFICATION_LEVELS:
            raise ValueError("Level sertifikasi tidak tersedia.")
        return value


class SalaryPredictionResponse(BaseModel):
    judul: str
    kategori: str
    lokasi: str
    pengalaman: str
    pendidikan: str
    sertifikasi: str
    gaji_basis: int
    gaji_setelah_koreksi_judul: int
    gaji_prediksi: int
    gaji_min: int
    gaji_max: int
    multiplier: float
    m_pengalaman: float
    m_pendidikan: float
    m_sertifikat: float
    m_koreksi_realistis: float
    m_koreksi_judul: float
    is_ambiguous_title: bool
    generic_tokens: list[str]
    confidence_label: str
    adjustment_notes: list[str]
    estimasi_kos: int
    rasio_kos: float


class SalaryEvaluationRequest(BaseModel):
    input_salary: int = Field(..., ge=0, examples=[7500000])
    prediction: SalaryPredictionResponse


class SalaryEvaluationResponse(BaseModel):
    input_salary: int
    status: dict
    delta_text: str
    bar_position: float
    range: dict


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)


class AiPredictionContext(BaseModel):
    judul: str | None = None
    kategori: str | None = None
    lokasi: str | None = None
    pengalaman: str | None = None
    pendidikan: str | None = None
    sertifikasi: str | None = None
    gaji_prediksi: int | None = None
    gaji_min: int | None = None
    gaji_max: int | None = None
    estimasi_kos: int | None = None
    rasio_kos: float | None = None


class AiChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list)
    prediction_context: AiPredictionContext | None = None


class AiChatResponse(BaseModel):
    reply: str
