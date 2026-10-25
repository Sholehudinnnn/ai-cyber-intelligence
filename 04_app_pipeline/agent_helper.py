AGENT_NAME = "AI Cyber Intelligence Analyst"


def _build_local_explanation(result):
    details = result["details"]
    input_summary = (
        f"{details['Percobaan login gagal']} percobaan login gagal; "
        f"perangkat belum dikenal: {details['Perangkat belum dikenal']}; "
        f"waktu akses tidak biasa: {details['Waktu akses tidak biasa']}; "
        f"akses ke bagian sensitif: {details['Akses ke bagian sensitif']}."
    )
    reasons = "; ".join(result["reasons"])
    recommendations = "; ".join(result["recommendations"])
    return (
        f"Dari input yang kamu berikan, tercatat {input_summary} "
        f"Model ML memprediksi tingkat risiko {result['level']} "
        f"(probabilitas kelas {result['score']}%). "
        f"Prediksi ini mempertimbangkan: {reasons} "
        f"Saran sesuai hasil tersebut: {recommendations} "
        "Prediksi ini adalah informasi pendukung, bukan kepastian adanya serangan."
    )


def explain_result(result):
    return {
        "available": True,
        "mode": "local",
        "agent_name": AGENT_NAME,
        "model": "GPT-4",
        "text": _build_local_explanation(result),
        "message": None,
    }
