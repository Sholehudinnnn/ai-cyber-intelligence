# AI Cyber Intelligence

Dashboard Flask untuk menganalisis indikator keamanan akun dan menampilkan
prediksi model ML, alasan, serta rekomendasi defensif. AI Analyst menjelaskan
hasil secara lokal berdasarkan input dan prediksi model; aplikasi tidak
mengirimkan data analisis ke layanan AI eksternal.

## Menjalankan aplikasi di Windows

Jalankan perintah berikut dari folder utama proyek:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\04_app_pipeline\requirements.txt
python .\04_app_pipeline\app.py
```

Buka `http://127.0.0.1:5000` di browser.

File model `04_app_pipeline/account_security_model.joblib` harus tersedia untuk
prediksi. Dataset berada di `data/account_security_dataset.csv` dan digunakan
untuk informasi evaluasi model.

## Website GitHub Pages

Website statis berada di `docs/` dan menjalankan model Random Forest langsung
di browser menggunakan `docs/model.json`. Model diekspor dari file scikit-learn
asli oleh `tools/export_static_model.py`; aplikasi tidak memerlukan server
Flask untuk inferensi di GitHub Pages.

GitHub Pages menerbitkan folder `docs/` dari branch `main`. URL situsnya:
`https://sholehudinnnn.github.io/ai-cyber-intelligence/`

Pipeline pelatihan dataset dapat dibuka di
[Google Colab](https://colab.research.google.com/drive/1qNHc-e5Ps7eYPS-8_GMR__p48A3f5uqt?usp=sharing).

Repo, kode situs, file model, dan dataset sintetis akan terlihat publik. Jangan
unggah `.env`, API key, kata sandi, atau data pribadi.
