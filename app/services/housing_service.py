import warnings

import numpy as np
import pandas as pd

from app.core.model_loader import load_housing_pipeline
from app.services.constants import COORDINATES


KOS_REGION_MAPPING = {
    "Bekasi": "Bekasi",
    "Bogor": "Bogor",
    "Depok": "Depok",
    "Jakarta Barat": "Jakarta Barat",
    "Jakarta Pusat": "Jakarta Pusat",
    "Jakarta Selatan": "Jakarta Selatan",
    "Jakarta Timur": "Jakarta Timur",
    "Jakarta Utara": "Jakarta Utara",
    "Tangerang": "Tangerang",
    "Tangerang Selatan": "Tangerang Selatan",
    "Jakarta Raya (General)": "Jakarta Selatan",
}


def predict_kos_price(region: str) -> int:
    """Predict monthly kos price using the legacy housing model inputs."""
    pipeline = load_housing_pipeline()
    region_value = KOS_REGION_MAPPING.get(region, "Jakarta Pusat")

    df_kos = pd.DataFrame(
        {
            "region": [region_value],
            "tipe_kos": ["Campur"],
            "is_electricity_included": ["Ya"],
            "rating_clean": [4.5],
            "rating_count_clean": [100],
            "room_area": [12.0],
        }
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        prediction = pipeline.predict(df_kos)[0]

    return int(np.expm1(prediction))


def calculate_distance(loc1: str, loc2: str) -> float:
    """Calculate straight-line distance in KM between two known locations."""
    from math import asin, cos, radians, sin, sqrt

    coord1 = COORDINATES.get(loc1)
    coord2 = COORDINATES.get(loc2)
    if not coord1 or not coord2:
        return 0

    lat1, lon1 = coord1
    lat2, lon2 = coord2
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return round(c * 6371, 1)


