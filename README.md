# HireVision FastAPI Backend

Backend ini adalah versi API bersih dari logic Streamlit lama. Model dan data memakai folder root project backend:

- `models/salary/`
- `models/kos/`
- `data/data_peta_jabodetabek.csv`

## Environment

Buat file `.env` di root backend:

```env
GEMINI_API_KEY=isi_key_gemini
```

Opsional:

```env
GEMINI_MODEL_NAME=gemini-2.5-flash
```

## Menjalankan Backend

Jalankan dari root project:

```bash
uvicorn app.main:app --reload
```

## Endpoint Awal

- `GET /api/health`
- `GET /api/metadata`
- `POST /api/salary/predict`
- `POST /api/salary/evaluate`
- `POST /api/ai/chat`
- `GET /api/spatial/summary`
- `GET /api/spatial/industry-distribution?category=IT,%20Tech%20%26%20Data`
