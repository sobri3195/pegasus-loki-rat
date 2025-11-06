
```
        ____  ________  ______   ________  ____  ___________ _________ 
       / __ \/ ____/  |/  /   | / ____/ / / /  |/  / ____/ //_/ ____/ / 
      / /_/ / __/ / /|_/ / /| |/ /   / /_/ / /|_/ / __/  ,<  \__ \ / /  
     / ____/ /___/ /  / / ___ / /___/ __  / /  / / /___/ /| |___/ // /___
    /_/   /_____/_/  /_/_/  |_\____/_/ /_/_/  /_/_____/_/ |_/____/_____/

               ⚡ Advanced BTS API Pentest Automation Tool ⚡
```

# Pegasus BTS Exploit

`pegasus-bts-exploit` adalah framework pentest otomatis yang dirancang khusus untuk menguji **API lokasi BTS (Base Transceiver Station)** dari provider jaringan seluler. Cocok digunakan oleh profesional keamanan siber yang memiliki **izin resmi**, proyek ini memudahkan pengujian dengan berbagai fitur canggih seperti injeksi payload, logging, analisis respons, hingga pembuatan laporan otomatis.

---

## 🚀 Fitur Unggulan

- ✅ Multi-threaded testing dengan auto-retry  
- ✅ Payload injeksi & XSS untuk deteksi celah  
- ✅ Deteksi anomali API & kebocoran data  
- ✅ Logging lengkap & laporan otomatis  
- ✅ Integrasi CI/CD pipeline (contoh: GitHub Actions)

---

## 📁 Struktur Folder

```
pegasus-bts-exploit/
├── README.md
├── requirements.txt
├── setup.sh
├── main.py
├── config/
│   └── config.py
├── payloads/
│   └── payload_list.txt
├── logs/
│   └── bts_api_pentest.log
├── utils/
│   ├── request_handler.py
│   ├── response_analyzer.py
│   └── report_generator.py
└── reports/
    └── summary_report.txt
```

---

## ⚙️ Cara Penggunaan

1. Clone repository ini:

```bash
git clone https://github.com/sobri3195/pegasus-bts-exploit.git
cd pegasus-bts-exploit
```

2. Jalankan setup:

```bash
chmod +x setup.sh
./setup.sh
```

3. Jalankan framework:

```bash
source venv/bin/activate
python main.py
```

📄 Laporan hasil pengujian dapat ditemukan di: `reports/summary_report.txt`

---

## 🔧 Konfigurasi

Edit file `config/config.py` sesuai kebutuhan:

```python
API_URL = "https://api.operator.com/bts/location"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
MAX_RETRIES = 3
THREAD_COUNT = 5
```

---

## 👨‍💻 Author

Letda Kes dr. Muhammad Sobri Maulana, S.Kom, CEH, OSCP, OSCE  
📧 Email: muhammadsobrimaulana31@gmail.com  
🌐 GitHub: [sobri3195](https://github.com/sobri3195)

---

## ☕ Donasi

Jika proyek ini membantumu, kamu bisa mendukung pengembangannya di:  
🔗 [https://lynk.id/muhsobrimaulana](https://lynk.id/muhsobrimaulana)

---

## ⚠️ Disclaimer

Proyek ini **hanya boleh digunakan untuk tujuan legal** dan **dengan izin resmi** dari pihak berwenang. Penulis **tidak bertanggung jawab atas penyalahgunaan** dalam bentuk apapun.

---

> “The quieter you become, the more you are able to hear.”  
> — *Rumi*
