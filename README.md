# Submission 1: Customer Churn Prediction
Nama: Muhammad Adha

Username dicoding: muhammad_adha

| | Deskripsi |
| ----------- | ----------- |
| Dataset | [Customer Churn Dataset (Synthetic)](https://github.com/adha20/ml-ops-submission) |
| Masalah | Banyak perusahaan kehilangan pendapatan karena pelanggan berhenti berlangganan layanan mereka (churn). Mengidentifikasi pelanggan yang kemungkinan besar akan *churn* secara manual sangat sulit, sehingga dibutuhkan pendekatan otomatis agar perusahaan dapat mengambil tindakan retensi secara proaktif. |
| Solusi machine learning | Mengembangkan model klasifikasi biner berbasis Deep Learning (TensorFlow/Keras) yang dibungkus dalam *machine learning pipeline* end-to-end otomatis menggunakan TensorFlow Extended (TFX). |
| Metode pengolahan | Data mentah (CSV) diproses menggunakan komponen TFX `Transform`. Fitur numerik (seperti `customer_age`, `monthly_charges`, `tenure`, `total_usage`) diskalakan menggunakan z-score (standardisasi). Fitur kategorikal (`gender`, `contract_type`) dikonversi menjadi representasi *vocabulary* numerik. |
| Arsitektur model | Model dibangun menggunakan Keras Sequential API dengan arsitektur Neural Network yang terdiri dari beberapa *hidden layer* `Dense` yang dipadukan dengan layer `Dropout` untuk mencegah *overfitting*, serta diakhiri dengan sebuah *output layer* beraktivasi `sigmoid` untuk memprediksi probabilitas *churn*. Hyperparameter (jumlah unit dan learning rate) dioptimasi secara otomatis menggunakan `KerasTuner` (metode `RandomSearch`). |
| Metrik evaluasi | Metrik utama yang digunakan pada TFX `Evaluator` adalah **BinaryAccuracy** dengan batas bawah kelulusan (threshold) ditetapkan sebesar 0.5 (50%), didukung oleh penghitungan ExampleCount, AUC, True Positives, dll. |
| Performa model | Model sukses di-*training* dan berhasil mendapatkan *blessing* (kelulusan) dari komponen TFX `Evaluator` karena metrik *BinaryAccuracy* mengungguli *baseline* dan memenuhi ambang batas yang dikonfigurasi pada *eval_config*. |
| Opsi deployment | Model final berformat *SavedModel* disajikan (*served*) menggunakan framework **FastAPI** di dalam kontainer **Docker**. Kontainer ini lalu di-*deploy* ke publik secara otomatis menggunakan integrasi CI/CD dari GitHub ke **Back4App Containers**. |
| Web app | [customer-churn-api](https://customerchurnapi-3h7jdnsm.b4a.run) |
| Monitoring | Monitoring dilakukan menggunakan library `prometheus_client` yang diintegrasikan ke FastAPI. Metrik seperti `customer_churn_requests_total` (total request) dan `customer_churn_request_latency_seconds` (latency) diekspos melalui endpoint `/metrics` yang berhasil di-*scrape* oleh server **Prometheus**. |

![Dashboard Monitoring](muhammad_adha-monitoring.png)
*(Gambar ini harus diganti dengan tangkapan layar asli hasil monitoring)*
