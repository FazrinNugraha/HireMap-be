from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.services.constants import (
    CATEGORIES,
    CERTIFICATION_LEVELS,
    EDUCATION_LEVELS,
    EXPERIENCE_LEVELS,
    LOCATIONS,
)


def _validate_option(value: str, options, error_message: str) -> str:
    """Validasi nilai request agar hanya memakai opsi resmi backend.

    Frontend memang mengambil opsi dari endpoint metadata, tetapi backend tetap
    perlu validasi sendiri untuk menjaga API aman jika ada request manual,
    request lama, atau input yang tidak sinkron dengan metadata terbaru.
    """
    if value not in options:
        raise ValueError(error_message)
    return value


class SalaryPredictionRequest(BaseModel):
    """Payload input dari form Salary Prediction.

    Model ini memastikan semua input yang masuk ke service salary sudah valid:
    job_title tidak kosong, kategori/lokasi tersedia, dan level profil user ada
    di constants.py. Jika salah satu tidak valid, FastAPI otomatis mengembalikan
    error 422 sebelum service ML dijalankan.
    """

    job_title: str = Field(..., min_length=1, examples=["Data Analyst"])
    category: str = Field(..., examples=["IT, Tech & Data"])
    location: str = Field(..., examples=["Jakarta Selatan"])
    experience_level: str = Field("Mid-Level (3-5 thn)", examples=["Mid-Level (3-5 thn)"])
    education_level: str = Field("S1 / Sarjana", examples=["S1 / Sarjana"])
    certification_level: str = Field("Tanpa Sertifikasi", examples=["Tanpa Sertifikasi"])

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        return _validate_option(value, CATEGORIES, "Kategori pekerjaan tidak tersedia.")

    @field_validator("location")
    @classmethod
    def validate_location(cls, value: str) -> str:
        return _validate_option(value, LOCATIONS, "Lokasi tidak tersedia.")

    @field_validator("experience_level")
    @classmethod
    def validate_experience_level(cls, value: str) -> str:
        return _validate_option(value, EXPERIENCE_LEVELS, "Level pengalaman tidak tersedia.")

    @field_validator("education_level")
    @classmethod
    def validate_education_level(cls, value: str) -> str:
        return _validate_option(value, EDUCATION_LEVELS, "Level pendidikan tidak tersedia.")

    @field_validator("certification_level")
    @classmethod
    def validate_certification_level(cls, value: str) -> str:
        return _validate_option(value, CERTIFICATION_LEVELS, "Level sertifikasi tidak tersedia.")


class SalaryPredictionResponse(BaseModel):
    """Response lengkap dari service prediksi gaji.

    Field response sengaja cukup detail karena dipakai oleh beberapa fitur:
    Salary Result memakai gaji_prediksi dan confidence, Housing memakai kos dan
    rasio_kos, Analisis Karir memakai multiplier, dan AI Consultant memakai
    konteks lengkap untuk membuat rekomendasi personal.
    """

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
    """Payload untuk mengecek salary user terhadap range prediksi."""

    input_salary: int = Field(..., ge=0, examples=[7500000])
    prediction: SalaryPredictionResponse


class SalaryEvaluationResponse(BaseModel):
    """Response visualisasi salary zone di frontend."""

    input_salary: int
    status: dict
    delta_text: str
    bar_position: float
    range: dict


class ChatMessage(BaseModel):
    """Satu pesan chat yang disimpan sebagai history AI Consultant."""

    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)


class AiPredictionContext(BaseModel):
    """Subset SalaryPredictionResponse yang aman dikirim sebagai konteks AI."""

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
    """Payload chat dari frontend ke AI Consultant."""

    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list)
    prediction_context: AiPredictionContext | None = None


class AiChatResponse(BaseModel):
    """Jawaban akhir dari AI Consultant."""

    reply: str
