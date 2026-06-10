from functools import lru_cache
import warnings

import joblib

from app.core.paths import MODELS_DIR
from app.services.constants import CATEGORIES, LOCATIONS


@lru_cache(maxsize=1)
def load_salary_resources() -> dict:
    """Load salary model artifacts once per process."""
    salary_dir = MODELS_DIR / "salary"

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = joblib.load(salary_dir / "salary_model_random_forest.pkl")
        tfidf_word = joblib.load(salary_dir / "tfidf_word_vectorizer.pkl")
        tfidf_char = joblib.load(salary_dir / "tfidf_char_vectorizer.pkl")
        target_encoder = joblib.load(salary_dir / "target_encoder.pkl")
        ohe_encoder = joblib.load(salary_dir / "ohe_encoder.pkl")

    return {
        "model": model,
        "tfidf_word": tfidf_word,
        "tfidf_char": tfidf_char,
        "target_encoder": target_encoder,
        "ohe_encoder": ohe_encoder,
        "list_lokasi": LOCATIONS,
        "list_kategori": CATEGORIES,
    }


@lru_cache(maxsize=1)
def load_housing_pipeline():
    """Load kos price pipeline once per process."""
    return joblib.load(MODELS_DIR / "kos" / "kos_price_pipeline.pkl")


