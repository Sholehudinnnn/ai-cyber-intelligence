
from predictor import predict_risk


def analyze_indicators(
    failed_logins,
    unknown_device,
    unusual_time,
    sensitive_access,
):
    # Prediksi menggunakan model yang dilatih di Google Colab.
    prediction = predict_risk(
        failed_logins,
        unknown_device,
        unusual_time,
        sensitive_access,
    )

    level = prediction["level"]

    recommendations_by_level = {
        "TINGGI": [
            "Pastikan aktivitas dilakukan oleh pengguna yang sah.",
            "Periksa log autentikasi dan waktu kejadian.",
            "Jika aktivitas tidak dikenal, hubungi administrator.",
        ],
        "SEDANG": [
            "Konfirmasi apakah perangkat dan waktu akses wajar.",
            "Tinjau riwayat login terkait.",
            "Aktifkan autentikasi multifaktor jika tersedia.",
        ],
        "RENDAH": [
            "Tetap gunakan kata sandi unik dan autentikasi multifaktor.",
            "Pantau aktivitas dan peringatan keamanan lainnya.",
        ],
    }

    titles = {
        "TINGGI": "Perlu pemeriksaan lebih lanjut",
        "SEDANG": "Perlu diverifikasi",
        "RENDAH": "Tidak banyak indikator risiko pada input",
    }

    reasons = []

    if failed_logins > 0:
        reasons.append(
            f"Terdapat {failed_logins} percobaan login gagal."
        )
    if unknown_device:
        reasons.append("Akses berasal dari perangkat yang belum dikenal.")
    if unusual_time:
        reasons.append("Akses terjadi pada waktu yang tidak biasa.")
    if sensitive_access:
        reasons.append("Aktivitas menyentuh bagian atau data sensitif.")

    if not reasons:
        reasons = ["Tidak ada indikator tambahan yang dipilih."]

    # Skor ditampilkan sebagai persentase probabilitas kelas
    # jika model menyediakan predict_proba.
    probabilities = prediction.get("probabilities", {})
    score = round(probabilities.get(level, 0) * 100)

    return {
        "score": score,
        "level": level,
        "title": titles[level],
        "reasons": reasons,
        "recommendations": recommendations_by_level[level],
        "is_demo": True,
        "model_prediction": prediction["prediction"],
        "probabilities": probabilities,
    }
