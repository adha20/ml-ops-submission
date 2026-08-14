# Proyek Akhir: Machine Learning Operations (MLOps)

## 1. Informasi Dataset
Dataset yang digunakan dalam proyek ini adalah data *Customer Churn* sintetis (customer_churn.csv) yang berisi atribut pelanggan seperti umur (`customer_age`), jenis kelamin (`gender`), tipe kontrak (`contract_type`), tagihan bulanan (`monthly_charges`), masa langganan (`tenure`), jumlah panggilan dukungan (`support_calls`), total penggunaan (`total_usage`), dan skor kepuasan (`satisfaction_score`). Target prediksinya adalah `churn` (1 = churn, 0 = tidak churn).

## 2. Persoalan yang Ingin Diselesaikan
Banyak perusahaan kehilangan pendapatan karena pelanggan berhenti menggunakan layanan mereka (churn). Mengidentifikasi pelanggan yang kemungkinan besar akan *churn* sangat penting agar perusahaan dapat mengambil tindakan proaktif seperti memberikan penawaran khusus atau kampanye retensi.

## 3. Solusi Machine Learning dan Target
Solusi yang dibuat adalah sebuah *Machine Learning Pipeline* end-to-end menggunakan **TensorFlow Extended (TFX)**. Model dilatih untuk mengklasifikasikan apakah seorang pelanggan akan churn atau tidak (Binary Classification). Target yang ingin dicapai adalah model yang memiliki nilai akurasi dan *recall* yang baik agar sistem tidak gagal mengidentifikasi pelanggan yang berisiko tinggi untuk churn.

## 4. Metode Pengolahan Data, Arsitektur Model, dan Metrik
- **Pengolahan Data**: Data divalidasi dan ditransformasi menggunakan komponen TFX (`ExampleGen`, `StatisticsGen`, `SchemaGen`, `ExampleValidator`, `Transform`). Fitur numerik di-skalakan menggunakan Z-score (`tft.scale_to_z_score`), sementara fitur kategorik (`gender`, `contract_type`) dikonversi menjadi nilai numerik yang terenkode.
- **Arsitektur Model**: Model menggunakan arsitektur *Deep Neural Network* dengan Keras Sequential API. Terdiri dari *Input Layer* untuk setiap fitur, lapisan *Concatenate*, dua *Hidden Layers* (Dense dengan aktivasi ReLU), dan sebuah *Output Layer* (Dense dengan aktivasi Sigmoid). *Hyperparameter Tuning* dilakukan menggunakan `KerasTuner` untuk mencari jumlah unit pada *hidden layer* dan *learning rate* terbaik.
- **Metrik Evaluasi**: Metrik yang digunakan adalah *Accuracy*, *Precision*, *Recall*, dan *AUC*. Batasan validasi di `Evaluator` menguji apakah *Binary Accuracy* model melebihi ambang batas (`>0.5`).

## 5. Performa Model
Setelah melakukan pelatihan dan *tuning*, model dievaluasi dan menunjukkan performa yang cukup baik. Anda dapat melihat hasil metrik akhir dari notebook. *(Catatan: Performa akhir dapat bervariasi bergantung pada hasil run)*.

## 6. Model Deployment
Model disajikan (*served*) menggunakan aplikasi **FastAPI** yang berjalan dalam *container Docker*. Aplikasi ini menyediakan endpoint REST API untuk menerima data pelanggan dan mengembalikan prediksi *churn*. Aplikasi di-*deploy* menggunakan layanan cloud seperti **Railway** / **Render** / **Heroku**.

## 7. Web App / API URL
Aplikasi di-deploy ke Back4App Containers dengan URL:
- https://customerchurnapi-3h7jdnsm.b4a.run

Anda bisa test API dengan endpoint:

## 8. Monitoring dengan Prometheus dan Grafana
Sistem monitoring dijalankan menggunakan **Prometheus** untuk mengumpulkan metrik dari endpoint `/metrics` di FastAPI, serta divisualisasikan menggunakan **Grafana**. Metrik yang dikumpulkan mencakup jumlah *request*, *latency*, dan penggunaan *resources* (*CPU/Memory*).

![Dashboard Monitoring](muhammad_adha-monitoring.png)
*(Gambar ini harus diganti dengan tangkapan layar asli hasil monitoring)*
