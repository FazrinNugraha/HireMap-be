import pandas as pd

from app.core.paths import DATA_DIR
from app.services.constants import COORDINATES
from app.services.housing_service import predict_kos_price


DEFAULT_COORDINATE = [-6.2000, 106.8166]


def get_location_coordinate(location: str) -> list[float]:
    """Ambil koordinat lokasi, fallback ke titik Jakarta jika tidak ditemukan.

    Data peta bergantung pada koordinat untuk menampilkan marker di frontend.
    Jika ada lokasi baru yang belum terdaftar di constants.COORDINATES, fallback
    ini menjaga API tetap mengembalikan lat/lon valid dan tidak membuat peta
    frontend error.
    """
    return COORDINATES.get(location, DEFAULT_COORDINATE)


def load_map_data() -> pd.DataFrame:
    """Load dataset peta Jabodetabek dan tambahkan koordinat marker.

    Dataset CSV menyimpan jumlah lowongan per lokasi/kategori. Frontend butuh
    lat/lon untuk menaruh marker di Leaflet, jadi service ini menambahkan kolom
    lat dan lon dari constants.COORDINATES setiap kali data dimuat.
    """
    df = pd.read_csv(DATA_DIR / "data_peta_jabodetabek.csv")
    df["lat"] = df["Lokasi_Clean"].apply(lambda x: get_location_coordinate(x)[0])
    df["lon"] = df["Lokasi_Clean"].apply(lambda x: get_location_coordinate(x)[1])
    return df


def get_spatial_summary() -> list[dict]:
    """Ringkasan wilayah untuk Spatial Map, commuter, dan ranking.

    Fungsi ini menggabungkan data lowongan per kota, lalu menambahkan estimasi
    harga kos dan koordinat. Outputnya menjadi sumber data utama frontend untuk:
    - marker peta,
    - tabel Regional Ranking,
    - opsi komuter,
    - beberapa kalkulasi DSS berbasis lokasi.
    """
    df_map = load_map_data()
    df_kota = df_map.groupby("Lokasi_Clean")["Jumlah_Lowongan"].sum().reset_index()
    df_kota["Harga_Kos_Estimasi"] = df_kota["Lokasi_Clean"].apply(predict_kos_price)
    df_kota["lat"] = df_kota["Lokasi_Clean"].apply(lambda x: get_location_coordinate(x)[0])
    df_kota["lon"] = df_kota["Lokasi_Clean"].apply(lambda x: get_location_coordinate(x)[1])
    df_kota = df_kota.sort_values(by="Jumlah_Lowongan", ascending=False)
    return df_kota.to_dict(orient="records")


def get_industry_distribution(category: str) -> list[dict]:
    """Ambil distribusi lowongan satu kategori di setiap lokasi.

    Fungsi ini berguna jika frontend ingin menampilkan sebaran industri tertentu.
    Data difilter berdasarkan kategori, dijumlahkan per kota, lalu diurutkan dari
    wilayah dengan lowongan paling banyak.
    """
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
    """Kembalikan detail lengkap untuk satu kota.

    Detail ini dipakai sidebar Spatial Map. Isinya:
    - total lowongan di kota tersebut,
    - estimasi kos kota tersebut,
    - jumlah lowongan kategori terpilih jika user memilih kategori tertentu,
    - top 3 kategori pekerjaan dengan demand paling tinggi,
    - koordinat lokasi untuk peta.
    """
    df_map = load_map_data()
    df_loc = df_map[df_map["Lokasi_Clean"] == location]

    total_jobs = int(df_loc["Jumlah_Lowongan"].sum())
    kos_estimasi = predict_kos_price(location)

    category_jobs = None
    if category and category != "All Industries":
        category_jobs = int(df_loc[df_loc["Kategori_Pekerjaan"] == category]["Jumlah_Lowongan"].sum())

    top_categories: list[str] = (
        df_loc.groupby("Kategori_Pekerjaan")["Jumlah_Lowongan"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
        .index.tolist()
        if not df_loc.empty
        else []
    )

    coords = get_location_coordinate(location)

    return {
        "lokasi": location,
        "total_jobs": total_jobs,
        "kos_estimasi": kos_estimasi,
        "category_jobs": category_jobs,
        "top_categories": top_categories,
        "lat": coords[0],
        "lon": coords[1],
    }



