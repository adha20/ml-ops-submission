# Panduan Deployment ke Back4App Containers dengan GitHub

Panduan lengkap step-by-step untuk mendeploy Customer Churn Prediction API ke Back4App Containers menggunakan GitHub.

---

## Prasyarat

Sebelum memulai, pastikan Anda sudah punya:
- Akun GitHub (gratis di https://github.com)
- Akun Back4App Containers (gratis di https://back4app.com)
- Git terinstall di komputer Anda
- Project folder `ml_ops_akhir` sudah siap di lokal

---

## STEP 1: Setup GitHub Repository

### 1.1 Buat Repository Baru di GitHub

1. Login ke GitHub (https://github.com/login)
2. Klik **+** di pojok kanan atas → pilih **New repository**
3. Isi nama repository: `ml-ops-submission` atau `customer-churn-mlops`
4. Pilih **Public** (agar Back4App Containers bisa mengakses)
5. **Jangan** pilih "Initialize this repository with..."
6. Klik **Create repository**

Hasilnya Anda akan mendapat URL seperti:
```
https://github.com/username_anda/ml-ops-submission.git
```

### 1.2 Inisialisasi Git di Folder Project Lokal

Buka PowerShell/Terminal dan navigasi ke folder project:

```powershell
cd "C:\Users\muham\Downloads\PEMBELAJARAN-EXTERNAL\DICODING\Project adha\ml_ops_akhir"
```

Inisialisasi Git:

```powershell
git init
git add .
git commit -m "Initial commit: MLOps submission with TFX pipeline and FastAPI serving"
```

### 1.3 Connect ke GitHub Repository

Hubungkan repository lokal ke GitHub (ganti `username_anda` dengan username GitHub Anda):

```powershell
git remote add origin https://github.com/username_anda/ml-ops-submission.git
git branch -M main
git push -u origin main
```

**Jika diminta username/password:**
- Username: username GitHub Anda
- Password: gunakan Personal Access Token (tidak password biasa)

**Cara buat Personal Access Token:**
1. Login GitHub → Settings (profile icon, kanan atas)
2. Developer settings → Personal access tokens → Tokens (classic)
3. Generate new token (classic)
4. Centang: `repo`, `workflow`
5. Copy token, gunakan sebagai password di git push

Setelah berhasil, cek di GitHub apakah semua file sudah terupload.

---

## STEP 2: Setup Back4App Containers Account dan Deployment

### 2.1 Daftar Akun Back4App Containers

1. Buka https://back4app.com
2. Klik **Sign Up**
3. Pilih cara daftar (GitHub, Email, atau yang lain)
4. **Jika pilih GitHub:** authorize Back4App Containers untuk akses account GitHub Anda

### 2.2 Buat Project Baru di Back4App Containers

1. Setelah login, Anda akan di halaman dashboard
2. Klik **New Project**
3. Pilih opsi **Deploy from GitHub repo**
4. Authorize Back4App Containers untuk akses GitHub (jika diminta)
5. Cari dan pilih repository `ml-ops-submission` Anda
6. Pilih branch: **main**
7. Klik **Deploy**

Back4App Containers akan mulai process:
- Pull code dari GitHub
- Build Docker image (sesuai Dockerfile di folder `app/`)
- Deploy container

Proses ini bisa memakan waktu 2-10 menit.

### 2.3 Konfigurasi Environment Variables di Back4App Containers

Setelah deployment selesai:

1. Di Back4App Containers dashboard, klik project Anda
2. Pilih tab **Variables** atau **Environment**
3. Tambahkan variable (jika ada yang diperlukan):
   - `PORT`: `8080` (default sudah ada)
   - `MODEL_PATH`: `/app/model_store/churn_model.joblib`

Kalau tidak ada tab khusus environment, Back4App Containers biasanya auto-detect dari `.env` atau config.

### 2.4 Tunggu Deployment Selesai

Cek status deployment di tab **Deployments** atau **Logs**:
- Status hijau = **Deployment berhasil**
- Status merah = ada error, cek logs untuk melihat error apa

---

## STEP 3: Dapatkan Deployment URL

### 3.1 Copy Public URL

Setelah deployment berhasil:

1. Di Back4App Containers dashboard, cari section **Service** atau **Deployment**
2. Akan ada URL seperti:
   ```
   https://ml-ops-submission-production.up.back4app.com
   ```

3. Copy URL ini

### 3.2 Test URL di Browser

Buka di browser:
```
https://ml-ops-submission-production.up.back4app.com/
```

Harusnya akan muncul response:
```json
{"message":"Customer churn prediction service is running."}
```

### 3.3 Test Prediction Endpoint

Gunakan tool seperti Postman atau curl untuk test endpoint `/predict`:

**Menggunakan PowerShell:**

```powershell
$url = "https://ml-ops-submission-production.up.back4app.com/predict"
$body = @{
    customer_age = 35
    gender = "Male"
    contract_type = "Month-to-Month"
    monthly_charges = 72.5
    tenure = 12
    support_calls = 4
    total_usage = 210
    satisfaction_score = 2
} | ConvertTo-Json

Invoke-RestMethod -Uri $url -Method Post -ContentType "application/json" -Body $body
```

Harusnya akan return:
```json
{
  "prediction": 1,
  "probability": 0.75,
  "label": "churn"
}
```

---

## STEP 4: Setup Monitoring dengan Prometheus

### 4.1 Deploy Prometheus ke Back4App Containers (Opsional)

Anda bisa deploy Prometheus ke Back4App Containers juga untuk monitoring:

1. Di Back4App Containers dashboard, buat **New Service**
2. Pilih **Docker**
3. Gunakan Dockerfile dari `monitoring/Dockerfile`
4. Deploy

Atau, Anda bisa menjalankan Prometheus secara lokal untuk testing.

### 4.2 Konfigurasi Prometheus untuk Target Cloud

Edit file `monitoring/prometheus.yml`:

Ganti line:
```yaml
static_configs:
  - targets: ['host.docker.internal:8080']
```

Menjadi:
```yaml
static_configs:
  - targets: ['ml-ops-submission-production.up.back4app.com']
```

(sesuaikan URL dengan URL deployment Back4App Containers Anda)

### 4.3 Jalankan Prometheus Lokal untuk Testing

Buka terminal baru, navigasi ke folder project:

```powershell
cd "C:\Users\muham\Downloads\PEMBELAJARAN-EXTERNAL\DICODING\Project adha\ml_ops_akhir"
docker run -d -p 9090:9090 -v "$(pwd)\monitoring\prometheus.yml:/etc/prometheus/prometheus.yml" prom/prometheus
```

Buka browser ke: `http://localhost:9090`

Di halaman **Status → Targets**, Anda akan lihat apakah API Anda bisa di-scrape.

---

## STEP 5: Ambil Screenshot Bukti Deployment

### 5.1 Screenshot URL Deployment Aktif

1. Buka URL deployment di browser
2. Ambil screenshot (tekan `Windows + Shift + S` di Windows)
3. Simpan dengan nama: `muhammad_adha-deployment.png`

Screenshot harus menunjukkan:
- URL deployment di address bar
- Response dari endpoint `/` atau `/predict` yang menunjukkan app running

### 5.2 Screenshot Deployment di Back4App Containers Dashboard

1. Buka Back4App Containers dashboard
2. Ambil screenshot halaman project yang menunjukkan:
   - Status deployment: **"Success"** atau **"Running"**
   - URL public app
   - Informasi deployment (tanggal, waktu, commit hash)

Simpan dengan nama: `muhammad_adha-deployment-dashboard.png`

---

## STEP 6: Update Dokumentasi dengan URL Asli

### 6.1 Edit README.md

Buka file `README.md` dan ganti section:

```markdown
## Web App / API URL
Example deployment URL:
- https://your-cloud-app-url.example.com
```

Menjadi:

```markdown
## Web App / API URL
Aplikasi di-deploy ke Back4App Containers dengan URL:
- https://ml-ops-submission-production.up.back4app.com

Anda bisa test API dengan endpoint:
- GET `/` → health check
- POST `/predict` → prediksi churn dengan input JSON
- GET `/metrics` → Prometheus metrics
```

### 6.2 Push Perubahan ke GitHub

```powershell
cd "C:\Users\muham\Downloads\PEMBELAJARAN-EXTERNAL\DICODING\Project adha\ml_ops_akhir"
git add README.md
git commit -m "Update deployment URL to Back4App Containers"
git push origin main
```

Back4App Containers akan otomatis re-deploy jika ada perubahan di main branch.

---

## STEP 7: Setup Monitoring dan Ambil Screenshot

### 7.1 Jalankan Prometheus dengan Docker (Lokal untuk Testing)

Jika Anda ingin test monitoring secara lokal sebelum submit:

```powershell
docker run -d `
  -p 9090:9090 `
  -v "$(pwd)\monitoring\prometheus.yml:/etc/prometheus/prometheus.yml" `
  --name prometheus-churn `
  prom/prometheus
```

Tunggu beberapa detik, lalu buka: `http://localhost:9090`

### 7.2 Cek Scraping Target

Di Prometheus dashboard:
1. Klik **Status** (menu atas)
2. Pilih **Targets**
3. Cek apakah target API Anda ada dan status **UP**

Jika status **DOWN**, berarti URL di `prometheus.yml` salah atau API tidak bisa diakses.

### 7.3 Query Metrics

Di halaman utama Prometheus:
1. Di input field, ketik: `customer_churn_requests_total`
2. Klik **Execute**
3. Anda akan lihat graph dan data metrics dari API

### 7.4 Ambil Screenshot Monitoring

1. Ambil screenshot halaman Prometheus yang menunjukkan metrics
2. Simpan dengan nama: `muhammad_adha-monitoring.png`

Screenshot harus menunjukkan:
- Halaman Prometheus dengan Targets yang UP
- Graph atau table dengan metrics dari API

---

## STEP 8 (OPSIONAL): Setup Grafana Dashboard

Jika ingin nilai lebih tinggi, Anda bisa setup Grafana:

### 8.1 Jalankan Grafana Lokal

```powershell
docker run -d -p 3000:3000 grafana/grafana
```

Buka: `http://localhost:3000`
- Login: admin / admin
- Change password saat diminta

### 8.2 Tambah Prometheus sebagai Data Source

1. Di Grafana, klik **Configuration** (gear icon)
2. Pilih **Data Sources**
3. Klik **Add data source**
4. Pilih **Prometheus**
5. URL: `http://localhost:9090`
6. Klik **Save & Test**

### 8.3 Buat Dashboard

1. Klik **+** → **Dashboard**
2. Klik **Add new panel**
3. Di query, pilih metric: `customer_churn_requests_total`
4. Kustomisasi title, legend, dll
5. Simpan dashboard dengan nama: `churn-monitoring`

### 8.4 Ambil Screenshot Grafana

Simpan dengan nama: `muhammad_adha-grafana-dashboard.png`

Screenshot harus menunjukkan:
- Dashboard Grafana dengan panel metrics
- Title dan legend yang jelas

---

## STEP 9: Persiapan File Final untuk Submission

### 9.1 Struktur Folder Final

Pastikan struktur seperti ini sebelum di-ZIP:

```
ml_ops_akhir/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── generate_customer_churn.py
│   └── customer_churn.csv
├── modules/
│   ├── __init__.py
│   ├── transform_module.py
│   └── trainer_module.py
├── muhammad_adha-pipeline/
│   └── pipeline.py
├── app/
│   ├── main.py
│   ├── Dockerfile
│   └── model_store/
├── monitoring/
│   ├── Dockerfile
│   ├── prometheus.yml
│   └── prometheus.config
├── muhammad_adha-testing.ipynb
├── muhammad_adha-deployment.png (screenshot)
├── muhammad_adha-monitoring.png (screenshot)
├── muhammad_adha-grafana-dashboard.png (optional)
└── muhammad_adha-pylint.png (optional, jika pakai pylint)
```

### 9.2 Ganti Nama Folder Sesuai Username Dicoding

**PENTING:** Ganti `muhammad_adha` dengan username Dicoding Anda yang **sebenarnya**.

Contoh jika username Dicoding Anda "miftah":
- `muhammad_adha-pipeline` → `miftah-pipeline`
- `muhammad_adha-testing.ipynb` → `miftah-testing.ipynb`
- `muhammad_adha-deployment.png` → `miftah-deployment.png`
- dll

### 9.3 Buat ZIP Final

Di PowerShell:

```powershell
cd "C:\Users\muham\Downloads\PEMBELAJARAN-EXTERNAL\DICODING\Project adha"
Compress-Archive -Path "ml_ops_akhir" -DestinationPath "ml_ops_submission_final.zip" -Force
```

Hasil: `ml_ops_submission_final.zip`

---

## STEP 10: Submit ke Dicoding

1. Login ke akun Dicoding Anda
2. Masuk ke kelas MLOps → Submission
3. Upload file `ml_ops_submission_final.zip`
4. Klik **Submit**
5. Tunggu review dari Tim Reviewer (maksimal 3 hari kerja)

---

## Troubleshooting

### Problem: Deployment di Back4App Containers Gagal

**Error di Logs:**
- `ModuleNotFoundError`: cek `requirements.txt` apakah semua dependency terinstall
- `FileNotFoundError`: cek path file, pastikan relatif ke working directory
- `ConnectionRefused`: API tidak bisa start, cek `app/main.py` syntax

**Solusi:**
1. Fix code lokal
2. Push ke GitHub: `git add . && git commit -m "Fix" && git push`
3. Back4App Containers akan otomatis re-deploy

### Problem: API URL Tidak Bisa Diakses

- Cek apakah Back4App Containers deployment status **Running** (hijau)
- Tunggu 1-2 menit setelah deploy selesai, baru test
- Cek firewall lokal tidak memblok akses keluar

### Problem: Prometheus Tidak Bisa Scrape Target

- Cek URL di `prometheus.yml` sudah benar (sesuai URL Back4App Containers)
- Cek endpoint `/metrics` ada di `app/main.py` (sudah ada di template)
- Kalau Prometheus lokal, URL target harus `http://host.docker.internal:8080` (bukan localhost)

---

## Checklist Sebelum Submit

- [ ] Repository GitHub sudah di-create dan push semua file
- [ ] Deployment ke Back4App Containers berhasil dan running
- [ ] URL deployment sudah ganti di README.md
- [ ] Test `/predict` endpoint via browser atau postman → berhasil
- [ ] Prometheus bisa scrape metrics dari API
- [ ] Screenshot deployment sudah diambil dan disimpan dengan nama benar
- [ ] Screenshot monitoring sudah diambil dan disimpan dengan nama benar
- [ ] Folder sesuai nama username Dicoding yang sebenarnya
- [ ] ZIP file tidak ZIP dalam ZIP
- [ ] Semua file .ipynb sudah dijalankan (bukan kosong)
- [ ] Siap submit ke Dicoding

---

## Support & Dokumentasi

Jika ada masalah:

- Back4App Containers Docs: https://docs.back4app.com
- GitHub Docs: https://docs.github.com
- FastAPI Docs: https://fastapi.tiangolo.com
- Prometheus Docs: https://prometheus.io/docs
- Dicoding Forum: https://www.dicoding.com/academies/443/discussions
