import pandas as pd

from app.core.paths import DATA_DIR
from app.services.constants import COORDINATES
from app.services.housing_service import predict_kos_price


def load_map_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "data_peta_jabodetabek.csv")
    df["lat"] = df["Lokasi_Clean"].apply(lambda x: COORDINATES.get(x, [-6.2000, 106.8166])[0])
    df["lon"] = df["Lokasi_Clean"].apply(lambda x: COORDINATES.get(x, [-6.2000, 106.8166])[1])
    return df


def get_spatial_summary() -> list[dict]:
    df_map = load_map_data()
    df_kota = df_map.groupby("Lokasi_Clean")["Jumlah_Lowongan"].sum().reset_index()
    df_kota["Harga_Kos_Estimasi"] = df_kota["Lokasi_Clean"].apply(predict_kos_price)
    df_kota["lat"] = df_kota["Lokasi_Clean"].apply(lambda x: COORDINATES.get(x, [-6.2000, 106.8166])[0])
    df_kota["lon"] = df_kota["Lokasi_Clean"].apply(lambda x: COORDINATES.get(x, [-6.2000, 106.8166])[1])
    df_kota = df_kota.sort_values(by="Jumlah_Lowongan", ascending=False)
    return df_kota.to_dict(orient="records")


def get_industry_distribution(category: str) -> list[dict]:
    df_map = load_map_data()
    df_industry = (
        df_map[df_map["Kategori_Pekerjaan"] == category]
        .groupby("Lokasi_Clean")["Jumlah_Lowongan"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    return df_industry.to_dict(orient="records")


def get_location_detail(location: str, category: str = None) -> dict:
    """Kembalikan detail lengkap untuk satu kota: total jobs, kos, top 3 kategori."""
    df_map = load_map_data()
    df_loc = df_map[df_map["Lokasi_Clean"] == location]

    total_jobs = int(df_loc["Jumlah_Lowongan"].sum())
    kos_estimasi = predict_kos_price(location)

    category_jobs = None
    if category and category != "All Industries":
        category_jobs = int(df_loc[df_loc["Kategori_Pekerjaan"] == category]["Jumlah_Lowongan"].sum())

    # Top 3 kategori berdasarkan jumlah lowongan
    top_categories: list[str] = (
        df_loc.groupby("Kategori_Pekerjaan")["Jumlah_Lowongan"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
        .index.tolist()
        if not df_loc.empty
        else []
    )

    coords = COORDINATES.get(location, [-6.2000, 106.8166])

    return {
        "lokasi": location,
        "total_jobs": total_jobs,
        "kos_estimasi": kos_estimasi,
        "category_jobs": category_jobs,
        "top_categories": top_categories,
        "lat": coords[0],
        "lon": coords[1],
    }



