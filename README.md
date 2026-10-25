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

## Deploy ke Render

File `render.yaml` menyediakan konfigurasi Web Service. Untuk membuat aplikasi
dapat diakses melalui URL publik:

1. Masuk ke Render dan pilih **New > Blueprint**.
2. Hubungkan akun GitHub dan beri Render akses ke repo Private
   `Sholehudinnnn/ai-cyber-intelligence`.
3. Pilih repo tersebut dan deploy Blueprint. Render akan memasang dependency,
   menjalankan Gunicorn, dan memeriksa endpoint `/health`.

Paket gratis Render dapat menghentikan layanan yang tidak aktif; permintaan
pertama setelah layanan tidur mungkin memerlukan waktu untuk menyala kembali.
Repo sumber tetap Private, tetapi aplikasi hasil deploy memiliki URL publik.
