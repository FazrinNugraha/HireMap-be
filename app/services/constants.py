# Daftar lokasi yang muncul di dropdown Salary Prediction dan Spatial Map.
LOCATIONS = [
    "Bekasi",
    "Bogor",
    "Depok",
    "Jakarta Barat",
    "Jakarta Pusat",
    "Jakarta Raya (General)",
    "Jakarta Selatan",
    "Jakarta Timur",
    "Jakarta Utara",
    "Tangerang",
    "Tangerang Selatan",
]

# Daftar kategori pekerjaan utama yang dipakai untuk filter, model, dan metadata.
CATEGORIES = [
    "Administrative & Customer Service",
    "Creative, Design & Media",
    "Engineering & Manufacturing",
    "Finance & Accounting",
    "HR & General Affairs",
    "Healthcare & Medical",
    "IT, Tech & Data",
    "Lainnya / Umum",
    "Logistics & Supply Chain",
    "Management & Supervisor",
    "Retail, F&B & Hospitality",
    "Sales & Marketing",
]

# Multiplier pengalaman untuk mengoreksi base salary dari model ML.
EXPERIENCE_LEVELS = {
    "Entry-Level (0-1 thn)": {"m_pengalaman": 0.80, "label": "Entry Level"},
    "Junior (1-3 thn)": {"m_pengalaman": 0.95, "label": "Junior"},
    "Mid-Level (3-5 thn)": {"m_pengalaman": 1.10, "label": "Mid-Level"},
    "Senior (5+ thn)": {"m_pengalaman": 1.20, "label": "Senior"},
}

# Multiplier pendidikan untuk menyesuaikan estimasi gaji berdasarkan pendidikan.
EDUCATION_LEVELS = {
    "SMA / SMK": {"m_pendidikan": 0.75, "label": "SMA/SMK"},
    "Diploma (D3/D4)": {"m_pendidikan": 0.90, "label": "Diploma"},
    "S1 / Sarjana": {"m_pendidikan": 1.00, "label": "S1/Sarjana"},
    "S2 / Magister ke atas": {"m_pendidikan": 1.10, "label": "S2+"},
}

# Multiplier sertifikasi untuk memberi efek tambahan pada profil user.
CERTIFICATION_LEVELS = {
    "Tanpa Sertifikasi": {"m_sertifikat": 1.00, "label": "None"},
    "Sertifikat Lokal / BNSP": {"m_sertifikat": 1.03, "label": "Lokal/BNSP"},
    "Sertifikat Global (Associate)": {"m_sertifikat": 1.05, "label": "Associate"},
    "Sertifikat Global (Expert)": {"m_sertifikat": 1.10, "label": "Expert"},
}

# Kata yang dianggap terlalu umum jika muncul sebagai judul pekerjaan.
# Contoh: "Staff" saja terlalu luas, sehingga confidence perlu diturunkan.
GENERIC_TITLE_TERMS = {
    "staff",
    "admin",
    "administrasi",
    "administrator",
    "assistant",
    "operator",
    "clerk",
    "crew",
    "helper",
    "support",
    "generalist",
    "general",
}

# Kata generik yang hanya ambigu pada kategori tertentu.
# Ini membantu sistem membaca konteks, misalnya "admin" lebih umum di Admin/HR.
GENERIC_CATEGORY_KEYWORDS = {
    "Administrative & Customer Service": {"staff", "admin", "administrasi", "assistant"},
    "HR & General Affairs": {"staff", "admin", "assistant", "generalist"},
    "Retail, F&B & Hospitality": {"crew", "staff", "helper"},
    "Logistics & Supply Chain": {"staff", "operator", "helper", "admin"},
}

# Lokasi non-prime dipakai untuk koreksi ekstra saat judul pekerjaan ambigu.
NON_PRIME_LOCATIONS = {"Bogor", "Depok", "Bekasi", "Tangerang", "Tangerang Selatan"}

# Koordinat kota untuk peta, perhitungan jarak, dan marker spatial.
COORDINATES = {
    "Jakarta Selatan": [-6.2615, 106.8106],
    "Jakarta Barat": [-6.1683, 106.7588],
    "Jakarta Utara": [-6.1384, 106.8643],
    "Jakarta Timur": [-6.2250, 106.9004],
    "Jakarta Pusat": [-6.1805, 106.8284],
    "Jakarta Raya (General)": [-6.2000, 106.8166],
    "Tangerang Selatan": [-6.2886, 106.7179],
    "Tangerang": [-6.1702, 106.6403],
    "Bekasi": [-6.2383, 106.9756],
    "Bogor": [-6.5971, 106.7996],
    "Depok": [-6.4025, 106.7942],
    "Luar Jabodetabek": [-6.2000, 106.8166],
}


