# HireVision Backend

This repository serves as the backend service for HireVision, providing a REST API built with FastAPI. It handles Machine Learning inference for salary and housing predictions, profile multiplier logic, and integration with the Google Gemini API for the AI consultant feature.

## Technology Stack

| Component | Technology |
|---|---|
| Framework | FastAPI (Python) |
| Machine Learning | Scikit-Learn, Pandas, Numpy, Joblib |
| Generative AI | Google Generative AI (Gemini) |
| Data Validation | Pydantic v2 |

## Core Architecture & Features

1. Machine Learning Pipeline
   - Salary Prediction: Utilizes a Random Forest Regressor trained on job titles (TF-IDF word and character n-grams) and categorical features (One-Hot Encoding for location, category, seniority).
   - Housing (Kos) Prediction: Utilizes a Random Forest pipeline to estimate average monthly room rental costs based on location and standard room specifications.

2. Rule-Based Corrections
   - Title Ambiguity Adjustments: Automatically detects generic job titles (e.g., "Staff", "Admin") and applies penalty multipliers to prevent overestimation.
   - Profile Multipliers: Adjusts the base salary prediction based on the user's experience level, education, and professional certifications.

3. Spatial & Commute Services
   - Loads static spatial data from `data/data_peta_jabodetabek.csv` to serve regional job vacancy rankings.
   - Calculates Haversine straight-line distances between Jabodetabek cities for commute simulations.

4. AI Integration
   - Constructs a dynamic system prompt containing the user's salary prediction context (base salary, housing cost, ratio).
   - Manages conversational history and forwards queries to the Gemini model.

## Environment Variables

Create a `.env` file in the root directory with the following variables:

| Variable | Description | Required | Default |
|---|---|---|---|
| GEMINI_API_KEY | API Key for Google Gemini AI | Yes | - |
| GEMINI_MODEL_NAME | Gemini model version to use | No | gemini-2.0-flash-lite |
| ALLOWED_ORIGINS | CORS allowed origins (comma separated) | No | http://localhost:5173 |

## Setup and Installation

1. Install Dependencies
   Ensure Python 3.10+ is installed.
   ```bash
   pip install -r requirements.txt
   ```

2. Required Assets
   Ensure the following directories and files exist in the root folder before starting the server:
   - `models/salary/`: Contains `.pkl` files for the salary model and encoders.
   - `models/kos/`: Contains the `.pkl` pipeline for housing prediction.
   - `data/data_peta_jabodetabek.csv`: Spatial statistics data.

3. Run Development Server
   ```bash
   uvicorn app.main:app --reload
   ```
   The API documentation (Swagger UI) will be automatically available at `http://127.0.0.1:8000/docs`.

## API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/metadata` | Retrieve dropdown options (locations, categories, levels). |
| POST | `/api/salary/predict` | Main endpoint. Returns salary prediction, kos estimation, and profile multipliers. |
| POST | `/api/salary/evaluate` | Evaluates a user-input salary against the predicted range. |
| POST | `/api/ai/chat` | Send a message to the AI Consultant using the prediction context. |
| GET | `/api/spatial/summary` | Aggregate data of job vacancies and housing costs per city. |
| GET | `/api/spatial/location-detail` | Detailed statistics for a specific city. |
