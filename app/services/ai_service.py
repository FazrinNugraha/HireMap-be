import os
from numbers import Number

from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-3.1-flash-lite")

BASE_SYSTEM_PROMPT = (
    "Anda adalah asisten konsultan karir profesional dan perencana keuangan untuk pencari kerja di Jabodetabek. "
    "Tugas Anda menjawab pertanyaan seputar karir, dan SECARA PROAKTIF memberikan 1-2 saran spesifik "
    "mengenai strategi finansial relokasi (tempat tinggal/kos) berdasarkan rasio gaji dan biaya hunian yang ada di konteks. "
    "Gunakan format jawaban yang rapi dan mudah dibaca: paragraf singkat atau bullet points pendek, hindari paragraf yang terlalu panjang, "
    "dan prioritaskan jawaban yang padat, jelas, dan langsung ke inti."
)


def _format_currency(value: int | float | None) -> str:
    """Format angka gaji/kos agar mudah dibaca di prompt AI.

    Fungsi ini hanya untuk teks prompt, bukan untuk perhitungan. Jika value tidak
    tersedia, prompt akan memakai tanda "-" supaya Gemini tetap mendapat kalimat
    yang stabil dan tidak error karena nilai None.
    """
    if value is None:
        return "-"
    return f"Rp {int(value):,}"


def build_system_prompt(prediction_context: dict | None = None) -> str:
    """Bangun system prompt Gemini berdasarkan konteks prediksi user.

    System prompt adalah instruksi dasar yang dibaca model sebelum menjawab chat.
    Di sini kita menggabungkan dua hal:
    1. BASE_SYSTEM_PROMPT, yaitu peran umum AI sebagai konsultan karir/finansial.
    2. prediction_context, yaitu hasil Salary Prediction terbaru milik user.

    Jika user belum menjalankan prediksi, AI tetap bisa menjawab pertanyaan umum.
    Jika konteks prediksi tersedia, AI akan diarahkan untuk memakai informasi
    posisi, lokasi, range gaji, estimasi kos, dan rasio kos sebagai dasar saran.
    """
    if not prediction_context:
        context_text = "Belum ada data prediksi gaji dari pengguna ini."
    else:
        context_text = (
            "Pengguna baru saja menggunakan fitur prediksi gaji dan mendapatkan hasil berikut: "
            f"Posisi/Jabatan: '{prediction_context.get('judul') or '-'}', "
            f"Kategori: {prediction_context.get('kategori') or '-'}, "
            f"Lokasi: {prediction_context.get('lokasi') or '-'}, "
            f"Pengalaman: {prediction_context.get('pengalaman') or '-'}, "
            f"Pendidikan: {prediction_context.get('pendidikan') or '-'}, "
            f"Sertifikasi Profesional: {prediction_context.get('sertifikasi') or '-'}, "
            f"estimasi gaji pasar setelah penyesuaian: {_format_currency(prediction_context.get('gaji_prediksi'))} per bulan "
            f"(rentang negosiasi wajar {_format_currency(prediction_context.get('gaji_min'))} "
            f"hingga {_format_currency(prediction_context.get('gaji_max'))}). "
            "Gunakan informasi ini sebagai konteks utama untuk semua jawaban Anda. "
        )

        if prediction_context.get("estimasi_kos") is not None:
            ratio = prediction_context.get("rasio_kos")
            ratio_text = f"{ratio:.1f}%" if isinstance(ratio, Number) else "-"
            context_text += (
                f"Selain itu, rata-rata harga kos di {prediction_context.get('lokasi') or 'lokasi tersebut'} "
                f"adalah {_format_currency(prediction_context.get('estimasi_kos'))} per bulan, "
                f"yang menghabiskan sekitar {ratio_text} dari prediksi gaji pengguna."
            )

    return f"{BASE_SYSTEM_PROMPT}\n\nKONTEKS PENGGUNA SAAT INI: {context_text}"


def _to_gemini_history(history: list[dict]) -> list[dict]:
    """Konversi history chat frontend ke format role yang diminta Gemini.

    Frontend menyimpan role sebagai "user" dan "assistant". Gemini memakai
    "user" dan "model", jadi message assistant perlu diganti menjadi model.
    Message kosong atau role yang tidak dikenal dilewati agar request ke Gemini
    tidak gagal karena format history yang tidak valid.
    """
    gemini_history = []
    for message in history:
        role = message.get("role")
        content = message.get("content")
        if not content or role not in {"user", "assistant"}:
            continue

        gemini_history.append(
            {
                "role": "model" if role == "assistant" else "user",
                "parts": [content],
            }
        )
    return gemini_history


def chat_with_career_consultant(
    message: str,
    history: list[dict] | None = None,
    prediction_context: dict | None = None,
) -> str:
    """Kirim pesan user ke Gemini dan kembalikan jawaban AI Consultant.

    Fungsi ini adalah service utama untuk endpoint chat. Urutannya:
    1. Ambil GEMINI_API_KEY dari environment.
    2. Configure SDK Gemini.
    3. Buat model dengan system_instruction dari build_system_prompt.
    4. Mulai chat dengan history yang sudah dikonversi.
    5. Kirim message terbaru.
    6. Validasi response supaya frontend tidak menerima jawaban kosong.

    prediction_context bersifat optional, tetapi ketika ada, jawaban AI akan jauh
    lebih personal karena tahu estimasi gaji, lokasi kerja, kos, dan rasio kos.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY belum tersedia di environment backend.")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        GEMINI_MODEL_NAME,
        system_instruction=build_system_prompt(prediction_context),
    )
    chat = model.start_chat(history=_to_gemini_history(history or []))
    response = chat.send_message(message)

    reply = getattr(response, "text", "") or ""
    if not reply.strip():
        raise RuntimeError("Gemini tidak mengembalikan jawaban.")

    return reply.strip()
