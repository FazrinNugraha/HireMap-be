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
    """Prediksi harga kos bulanan untuk satu region.

    Model housing lama membutuhkan beberapa fitur kos, bukan hanya nama kota.
    Karena fitur frontend saat ini hanya memilih lokasi kerja, service ini
    membuat input standar yang dianggap representatif:
    - tipe kos: Campur,
    - listrik termasuk,
    - rating 4.5 dengan 100 review,
    - luas kamar 12 m2.

    Nilai region juga dipetakan lewat KOS_REGION_MAPPING karena beberapa label
    aplikasi tidak selalu sama persis dengan label training model. Contohnya,
    "Jakarta Raya (General)" diarahkan ke "Jakarta Selatan" sebagai fallback
    yang relatif representatif.
    """
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
    """Hitung jarak garis lurus antar dua lokasi dalam kilometer.

    Fungsi ini memakai rumus Haversine, yaitu pendekatan jarak berdasarkan titik
    koordinat latitude/longitude. Hasilnya bukan jarak jalan real-time, tetapi
    cukup untuk scoring awal seperti DSS commute atau estimasi cepat antar kota.

    Jika salah satu lokasi tidak ada di COORDINATES, fungsi mengembalikan 0 agar
    caller tidak gagal. Artinya caller perlu memahami 0 sebagai fallback, bukan
    selalu berarti lokasi benar-benar sama.
    """
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

