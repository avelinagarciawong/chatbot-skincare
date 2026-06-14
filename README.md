# Chatbot Skincare - Shopee Scraper & Setup

Repository ini berisi tools untuk melakukan scraping data produk skincare dari Shopee (menggunakan Selenium & `undetected-chromedriver` untuk melewati deteksi bot) serta memproses data untuk chatbot skincare.

## Persyaratan Awal (Prerequisites)
- **Python 3.10 ke atas** (Direkomendasikan Python 3.11 atau 3.12/3.13)
- **Google Chrome** terinstall di perangkat Anda.

---

## 💻 Panduan Instalasi & Menjalankan di macOS

### 1. Buat & Aktifkan Virtual Environment
Buka Terminal di folder project ini:
```bash
# Membuat virtual environment
python3 -m venv .venv

# Mengaktifkan virtual environment
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

> [!NOTE]  
> Jika Anda menemui error SSL saat pertama kali mengunduh file browser webdriver di Mac, jalankan perintah di bawah ini untuk menginstal sertifikat SSL Python:
> ```bash
> open "/Applications/Python 3.13/Install Certificates.command"
> ```
> *(Ganti `3.13` sesuai dengan versi Python yang Anda install)*

### 3. Verifikasi Setup & Jalankan Program
Untuk memastikan semua library (seperti ChromaDB dan Groq API) sudah siap:
```bash
python 01_test_setup.py
```

Untuk menjalankan scraper Shopee:
```bash
python 02_scrape_shopee.py
```

---

## 🔌 Panduan Instalasi & Menjalankan di Windows

### 1. Buat & Aktifkan Virtual Environment
Buka Command Prompt (cmd) atau PowerShell di folder project:

**Menggunakan Command Prompt (cmd):**
```cmd
:: Membuat virtual environment
python -m venv .venv

:: Mengaktifkan virtual environment
.venv\Scripts\activate.bat
```

**Menggunakan PowerShell:**
```powershell
# Membuat virtual environment
python -m venv .venv

# Mengaktifkan virtual environment
.venv\Scripts\Activate.ps1
```
*(Jika muncul error Permission di PowerShell, jalankan `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` terlebih dahulu).*

### 2. Install Dependencies
```cmd
pip install -r requirements.txt
```

### 3. Verifikasi Setup & Jalankan Program
```cmd
python 01_test_setup.py
```

Untuk menjalankan scraper Shopee:
```cmd
python 02_scrape_shopee.py
```

---

## 💡 Tips Penggunaan Scraper (`02_scrape_shopee.py`)

1. **Bypass Verifikasi/Login Wall**:
   Saat script pertama kali dijalankan, script akan membuka Chrome dan memunculkan petunjuk di Terminal:
   ```text
   SILAKAN LOGIN / SELESAIKAN VERIFIKASI DI BROWSER CHROME SEKARANG
   ```
   Silakan lakukan login atau selesaikan slide captcha pada jendela Chrome yang terbuka. Setelah Anda masuk ke beranda Shopee, kembali ke Terminal Anda dan tekan **ENTER** untuk mulai scraping otomatis.
   
2. **Kustomisasi Keyword**:
   Anda bisa mengubah kata kunci pencarian pada list `KEYWORDS` di bagian atas file [02_scrape_shopee.py](file:///Users/alex/Workspace/chatbot-skincare/02_scrape_shopee.py).

3. **Output File**:
   Hasil scraping akan disimpan secara otomatis di folder:
   - `data/raw_shopee_produk.csv` (data produk)
   - `data/raw_shopee_ulasan.csv` (data ulasan pembeli)
