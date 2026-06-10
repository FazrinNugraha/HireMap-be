import os
from numbers import Number

from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")

BASE_SYSTEM_PROMPT = (
    "Anda adalah asisten konsultan karir profesional dan perencana keuangan untuk pencari kerja di Jabodetabek. "
    "Tugas Anda menjawab pertanyaan seputar karir, dan SECARA PROAKTIF memberikan 1-2 saran spesifik "
    "mengenai strategi finansial relokasi (tempat tinggal/kos) berdasarkan rasio gaji dan biaya hunian yang ada di konteks. "
    "Gunakan format jawaban yang rapi dan mudah dibaca: paragraf singkat atau bullet points pendek, hindari paragraf yang terlalu panjang, "
    "dan prioritaskan jawaban yang padat, jelas, dan langsung ke inti."
)


def _format_currency(value: int | float | None) -> str:
    if value is None:
        return "-"
    return f"Rp {int(value):,}"


def build_system_prompt(prediction_context: dict | None = None) -> str:
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
