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

## GitHub

Repo GitHub hanya menyimpan kode dan file proyek. Repo Private membatasi akses
ke pemilik dan kolaborator yang diundang; repo ini tidak membuat aplikasi
tersedia sebagai situs web publik. Jangan unggah `.env`, API key, kata sandi,
atau data pribadi.
