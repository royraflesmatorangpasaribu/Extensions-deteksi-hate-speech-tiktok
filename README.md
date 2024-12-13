# Deteksi Hate Speech pada Komentar TikTok

Plugin ini digunakan untuk mendeteksi konten hate speech pada kolom komentar TikTok.

## Langkah-langkah Instalasi

### 1. Clone Repository
Clone repository ini ke dalam mesin lokal Anda menggunakan perintah berikut:

```bash
git clone https://github.com/royraflesmatorangpasaribu/extensions-deteksi-hate-speech-tiktok.git
```

### 2. Instalasi Dependensi
Pastikan sudah memiliki python versi 3.11.4 jika tidak ada silahkan download : https://www.python.org/downloads/release/python-3114/
Setelah repository berhasil di-clone, masuk ke dalam direktori proyek (api-extension-hatespeech-detector-v1) dan install semua dependensi yang diperlukan dengan perintah:
```bash
pip install -r requirements.txt
```

### 3. Mengunduh Data NLTK
Setelah instalasi selesai, Anda perlu mengunduh data yang diperlukan oleh NLTK (Natural Language Toolkit).

Buka Python shell di terminal atau Command Prompt dengan menjalankan perintah:
```bash
python
```
Di dalam Python shell, jalankan perintah berikut untuk mengunduh punkt dan punkt_tab:
```bash
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
```

### 4. Buka Halaman Extensions di Google Chrome
- Buka Google Chrome.
- Di bagian kanan atas, klik ikon tiga titik vertikal (menu).
- Pilih **More tools** > **Extensions**.

Alternatifnya, Anda bisa mengetik `chrome://extensions` di address bar dan tekan Enter.

### 5. Aktifkan "Developer mode"
Di halaman Extensions, aktifkan opsi **Developer mode** yang ada di pojok kanan atas.

### 6. Muat Ekstensi Unpacked
- Klik tombol **Load unpacked**.
- Pilih folder yang berisi file ekstensi (extension-tiktok-hatespeech-detector-v1).
- Setelah memilih folder, ekstensi akan langsung dimuat dan ditambahkan ke daftar ekstensi yang aktif di browser Anda.

### 7. Menjalankan API
Setelah semuanya terinstal, jalankan API (api-extension-hatespeech-detector-v1) menggunakan Uvicorn dengan perintah berikut:
```bash
uvicorn app:app --reload
```
