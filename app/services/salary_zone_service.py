def get_salary_zone_status(input_salary: int, prediction: dict) -> dict:
    """Tentukan status salary user terhadap range prediksi sistem.

    Fungsi ini membandingkan input_salary dengan tiga angka penting dari hasil
    prediksi:
    - gaji_min: batas bawah negosiasi wajar,
    - gaji_prediksi: titik estimasi utama model,
    - gaji_max: batas atas negosiasi wajar.

    Output label/level/desc dipakai frontend untuk memberi interpretasi cepat:
    apakah salary terlalu rendah, masih aman, ideal, atau sudah terlalu optimis.
    """
    gaji_min = prediction["gaji_min"]
    gaji_prediksi = prediction["gaji_prediksi"]
    gaji_max = prediction["gaji_max"]

    if input_salary < gaji_min:
        return {
            "label": "DI BAWAH PASAR",
            "level": "low",
            "desc": "Angka ini masih berada di bawah kisaran wajar sistem. Sebaiknya pertimbangkan negosiasi agar hasil akhirnya lebih kompetitif.",
        }

    if input_salary < gaji_prediksi:
        return {
            "label": "BATAS BAWAH",
            "level": "caution",
            "desc": "Angka ini masih aman dan realistis, tetapi belum menyentuh titik estimasi terbaik untuk profil Anda.",
        }

    if input_salary <= gaji_max:
        return {
            "label": "KISARAN WAJAR",
            "level": "ideal",
            "desc": "Angka ini berada di zona negosiasi yang ideal. Cukup kuat untuk diajukan, namun masih terlihat realistis untuk profil Anda.",
        }

    return {
        "label": "DIATAS PASAR",
        "level": "optimistic",
        "desc": "Angka ini sudah melewati batas atas kisaran wajar. Masih bisa dipakai sebagai target optimistis, tetapi perlu alasan negosiasi yang kuat.",
    }


def evaluate_salary(input_salary: int, prediction: dict) -> dict:
    """Bangun evaluasi lengkap salary untuk visualisasi frontend.

    get_salary_zone_status hanya menentukan kategori status. Fungsi ini
    menambahkan informasi pendukung:
    - delta_text: selisih input dengan batas bawah/atas,
    - bar_position: posisi salary pada progress bar frontend,
    - range: angka min, estimasi, dan max yang ditampilkan ke user.

    Bar position sengaja memakai rentang visual yang sedikit lebih lebar
    (85% dari min sampai 115% dari max) agar angka di luar range tetap bisa
    terlihat proporsional di UI.
    """
    status = get_salary_zone_status(input_salary, prediction)
    gaji_min = prediction["gaji_min"]
    gaji_prediksi = prediction["gaji_prediksi"]
    gaji_max = prediction["gaji_max"]

    if input_salary < gaji_min:
        delta_text = f"-Rp {int(gaji_min - input_salary):,} dari batas bawah"
    elif input_salary > gaji_max:
        delta_text = f"+Rp {int(input_salary - gaji_max):,} di atas batas atas"
    else:
        delta_text = "Berada dalam kisaran negosiasi"

    range_min = gaji_min * 0.85
    range_max = gaji_max * 1.15
    pct_bar = min(max((input_salary - range_min) / (range_max - range_min), 0), 1)

    return {
        "input_salary": input_salary,
        "status": status,
        "delta_text": delta_text,
        "bar_position": round(pct_bar, 4),
        "range": {
            "min_wajar": gaji_min,
            "estimasi": gaji_prediksi,
            "max_nego": gaji_max,
        },
    }
