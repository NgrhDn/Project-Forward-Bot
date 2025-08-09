# 🤖 Project Forward Bot Telegram

Bot otomatis untuk memforward media (foto, video, dan GIF) dari channel Telegram ke grup/tujuan tertentu dengan **AUTO-RECONNECT**, **SMART PAUSE SYSTEM**, dan optimasi khusus untuk **Termux/Android**.

---

## 📦 Fitur Utama

- ✅ **Auto-Reconnect**: Tidak pernah berhenti karena masalah jaringan
- ✅ **Smart Pause System**: Auto-pause saat memory penuh dengan interactive resume
- ✅ **Perfect Anti-Duplicate**: Per-message ID tracking yang tidak pernah duplicate
- ✅ **Memory Monitoring**: Real-time memory monitoring dengan auto-pause threshold
- ✅ **Interactive Controls**: Pause/resume/quit controls yang responsive
- ✅ **Auto Log Management**: Otomatis setup folder log baru saat ganti source channel
- ✅ **Termux Optimized**: Dioptimasi khusus untuk Android/Termux environment
- ✅ **FloodWait Handling**: Handle rate limiting Telegram dengan sempurna
- ✅ **Real-time Monitoring**: Forward otomatis saat ada media baru
- ✅ **Batch Processing**: Scan semua pesan lama atau sejumlah tertentu
- ✅ **Connection Monitor**: Monitor koneksi real-time setiap 20 detik
- ✅ **Graceful Shutdown**: Berhenti dengan aman menggunakan Ctrl+C
- ✅ **Helper Scripts**: setup_channel.py untuk easy channel switching

## 🆕 Fitur Terbaru (v2.1.0)

- ⏸️ **Smart Pause System**: Auto-pause saat memory penuh dengan interactive resume controls
- 🆔 **Perfect Anti-Duplicate**: Per-message ID tracking yang tidak pernah duplicate meskipun restart
- 📁 **Auto Log Management**: Otomatis backup log lama dan setup folder log baru saat ganti source channel  
- 🔧 **Memory Monitoring**: Real-time memory monitoring dengan threshold auto-pause (< 100MB atau > 90% usage)
- 🎮 **Interactive Controls**: Pause/resume/quit controls dengan pilihan c/q/m yang responsive
- 💾 **Smart ID Management**: Improved ID tracking dan file handling dengan UTF-8 encoding
- 📊 **Better Progress Display**: Progress tracking dengan memory status real-time setiap 25 pesan
- 🛠️ **Helper Scripts**: setup_channel.py untuk easy channel switching dan auto-backup
- 🔄 **Batch Optimization**: Smaller batch size (25) untuk optimal Termux performance
- 📱 **Enhanced Mobile Support**: Better resource management untuk Android/Termux environment

---

## 🚀 Instalasi & Jalankan

### 📱 **Untuk Termux (Android) - RECOMMENDED**

#### 1. Clone & Setup
```bash
git clone https://github.com/NgrhDn/Project-Forward-Bot.git
cd Project-Forward-Bot

# Jalankan setup otomatis (sekali saja)
chmod +x setup_termux.sh
./setup_termux.sh
```

#### 2. Konfigurasi Channel
```bash
# Gunakan helper script (recommended)
python setup_channel.py

# Atau manual edit main.py
```

#### 3. Jalankan Bot
```bash
# Simple (Recommended)
python main.py

# Dengan Auto-Restart
chmod +x run_termux.sh
./run_termux.sh
```

### 💻 **Untuk Windows**

#### 1. Clone & Install
```bash
git clone https://github.com/NgrhDn/Project-Forward-Bot.git
cd Project-Forward-Bot
pip install -r requirements.txt
```

#### 2. Konfigurasi
```bash
# Setup channel dengan helper script
python setup_channel.py
```

#### 3. Jalankan
```bash
# Simple
python main.py

# Dengan Auto-Restart
python run_bot.py

# Atau double-click
start_bot.bat
```

### 🐧 **Untuk Linux/VPS**

```bash
git clone https://github.com/NgrhDn/Project-Forward-Bot.git
cd Project-Forward-Bot
pip install -r requirements.txt
python setup_channel.py  # Setup channel
python main.py           # Jalankan bot
```

---

## ⚙️ Konfigurasi

### 1. **Mendapatkan API Credentials**
- Kunjungi [my.telegram.org](https://my.telegram.org)
- Login dengan nomor Telegram
- Buat aplikasi baru
- Salin `api_id` dan `api_hash`

### 2. **Setup Channel dengan Helper Script (RECOMMENDED)**
```bash
# Jalankan helper script
python setup_channel.py

# Script akan meminta:
# - Source channel ID (channel sumber)
# - Target channel ID (grup/channel tujuan)
# 
# Dan otomatis:
# ✅ Backup log lama ke logs_backup/
# ✅ Buat folder log baru
# ✅ Update konfigurasi main.py
# ✅ Ready to run!
```

### 3. **Manual Setup (Alternative)**
Edit `main.py` secara manual:
```python
# === Konfigurasi API ===
api_id = 12345678  # Your API ID
api_hash = 'your_api_hash_here'

# === ID Channel dan Grup ===
source_channel = -1001234567890  # Channel sumber
target_channel = -1009876543210  # Grup/channel tujuan
```

---

## 🎮 Cara Penggunaan

### **Mode Scanning**
1. **Scan Semua**: Scan semua pesan dari awal channel
2. **Scan Terbatas**: Scan sejumlah pesan terakhir (contoh: 1000)
3. **Real-time Only**: Langsung ke mode real-time tanpa scan

### **Interactive Controls (NEW!)**
Bot dilengkapi dengan sistem kontrol interaktif:

**Saat Memory Penuh:**
```
⏸️ BOT DIJEDA: Memory penuh - 45MB tersisa (95.2% used)
🔧 Silakan bersihkan memory/storage atau perbaiki masalah
⚡ Ketik 'c' + Enter untuk melanjutkan setelah masalah diperbaiki

💡 Pilihan:
   c = Continue (lanjutkan setelah bersihkan memory)
   q = Quit (keluar dari bot)
   m = Check memory status

Pilihan (c/q/m): _
```

**Controls Available:**
- **c** = Continue (lanjutkan setelah pause)
- **q** = Quit (keluar dari bot)  
- **m** = Memory check (cek status memory)
- **Ctrl+C** = Graceful shutdown

### **Ganti Source Channel**
```bash
# Gunakan helper script (SANGAT MUDAH!)
python setup_channel.py

# Otomatis:
# 1. Input channel ID baru
# 2. Backup log lama ke logs_backup/
# 3. Buat folder log baru
# 4. Update main.py
# 5. Siap dijalankan!
```

### **Monitor Progress dengan Memory Status**
```
📊 Progress: 25/1000 | Memory OK: 150MB tersisa (75.2% used)
[25 dari 1000] ✅ Dikirim (ID: 12345) 📥 Scan
🛑 Delay 20 detik untuk keamanan (per 25 pesan)...
```

---

## 📱 Tips Khusus Termux

### **Optimasi Android**
1. **Disable Battery Optimization**:
   - Settings → Apps → Termux → Battery → Don't optimize

2. **Keep Termux Active**:
   - Jangan minimize terlalu lama
   - Pin Termux di recent apps

3. **Network Stability**:
   - Gunakan WiFi stabil
   - Hindari mobile data yang tidak stabil

4. **Memory Management**:
   - Bot otomatis pause saat memory < 100MB
   - Bersihkan storage secara berkala
   - Tutup aplikasi lain yang tidak perlu

5. **Permissions & Setup**:
   ```bash
   # Install Termux API untuk wake lock
   pkg install termux-api
   
   # Grant storage permission
   termux-setup-storage
   
   # Install psutil untuk memory monitoring
   pip install psutil
   ```

---

## 🛠️ Troubleshooting

### **Memory Full Issues (NEW!)**
```
⏸️ BOT DIJEDA: Memory penuh - 50MB tersisa (92.1% used)
🔧 Silakan bersihkan memory/storage atau perbaiki masalah

✅ SOLUSI: 
1. Bersihkan storage/memory HP
2. Tutup aplikasi lain yang tidak perlu  
3. Hapus file tidak perlu
4. Ketik 'c' untuk melanjutkan
```

### **Connection Issues**
```
❌ ConnectionError: Connection to Telegram failed
✅ SOLUSI: Bot akan auto-reconnect, tunggu saja
```

### **FloodWait Errors**
```
❌ FloodWaitError: Too many requests
✅ SOLUSI: Bot akan otomatis pause dan resume setelah delay
```

### **Duplicate Messages**
```
♻️ Lewat (ID: 12347) Sudah pernah dikirim
✅ SOLUSI: Bot otomatis skip pesan yang sudah dikirim (Perfect!)
```

### **Permission Denied (Termux)**
```bash
chmod +x *.sh
```

### **Module Not Found**
```bash
pip install -r requirements.txt --upgrade
```

---

## 📊 Monitoring & Logs

### **File Log Structure**
```
logs/
├── {source_channel_id}/
│   ├── forwarded_ids.txt    # ID pesan yang sudah dikirim
│   ├── failed_ids.txt       # ID pesan yang gagal
│   └── log.txt             # Log aktivitas lengkap
└── logs_backup/            # Backup otomatis log lama
    └── {old_channel}_{timestamp}/
```

### **Real-time Status Display**
```
✅ Dikirim (ID: 12345) 📥 Realtime
❌ Gagal kirim ID 12346 
♻️ Lewat (ID: 12347) Sudah pernah dikirim
🔄 Retry batch 10 media gagal...
📡 Koneksi pulih!
📊 Progress: 25/1000 | Memory OK: 150MB tersisa (75.2% used)
⏸️ BOT DIJEDA: Memory penuh - bersihkan storage
💾 Saved forwarded ID: 12348
🗑️ Removed from failed list: 12349
```

### **Memory Monitoring Display**
```
📊 Memory OK: 250MB tersisa (65.5% used)
📊 Memory rendah: 80MB tersisa (92.1% used)
⏸️ BOT DIJEDA: Memory penuh - 45MB tersisa (95.2% used)
```

---

## 🔧 Advanced Configuration

### **Memory Threshold Customization**
```python
# Edit di check_memory_usage() function
if available_mb < 100 or used_percent > 90:  # Threshold default
    return False, "Memory rendah"

# Bisa diubah sesuai kebutuhan:
# available_mb < 200  # Untuk threshold 200MB
# used_percent > 85   # Untuk threshold 85%
```

### **Batch Size Optimization**
```python
# Edit di berbagai bagian kode
retry_batch = list(failed_ids)[:25]  # Default: 25 untuk Termux
# Bisa diubah ke 50 untuk PC yang lebih powerful

# Memory check interval
if count % 25 == 0:  # Default: setiap 25 pesan
# Bisa diubah ke 50 atau 100 untuk device powerful
```

### **Auto Log Management**
- Log otomatis terpisah per channel ID
- Backup otomatis saat ganti channel dengan timestamp
- Struktur: `logs/{channel_id}/` dan `logs_backup/{old_channel}_{timestamp}/`
- Helper script `setup_channel.py` untuk easy switching

---

## 📋 Requirements

### **Minimum System**
- Python 3.7+
- 100MB free storage minimum (untuk log dan cache)
- 512MB RAM minimum (1GB recommended)
- Internet connection (WiFi recommended untuk Termux)

### **Dependencies**
```
telethon==1.40.0
psutil>=5.8.0 (untuk memory monitoring)
```

### **Optional (Termux)**
```
termux-api (untuk wake lock)
```

---

## 🛠️ Helper Scripts

### **setup_channel.py** (NEW!)
Script untuk mengganti source channel dengan mudah:
```bash
python setup_channel.py

# Fitur:
✅ Input channel ID baru dengan validasi
✅ Backup log lama otomatis ke logs_backup/
✅ Buat folder log baru dengan struktur lengkap
✅ Update konfigurasi main.py otomatis
✅ Backup main.py sebelum edit
✅ Setup lengkap untuk channel baru
✅ Ready to run langsung setelah setup
```

### **Memory Management** (NEW!)
Bot secara otomatis:
- Monitor memory setiap 25 pesan
- Pause saat memory < 100MB atau usage > 90%
- Berikan kontrol interaktif untuk resume
- Log status memory di setiap progress update
- Cross-platform: psutil + /proc/meminfo fallback

### **Auto-Restart Scripts**
```bash
# Termux
./run_termux.sh          # Advanced dengan monitoring
nohup ./run_termux.sh &  # Background mode

# Windows  
start_bot.bat            # Batch file auto-restart
python run_bot.py        # Python auto-restart

# Linux
python run_bot.py        # Python auto-restart
```

---

## 🤝 Contributing

Kontribusi sangat diterima! Silakan:

1. Fork repository
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buka Pull Request

**Areas yang membutuhkan kontribusi:**
- Multi-language support
- GUI interface
- Database integration  
- Advanced filtering options
- Performance optimizations

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🙏 Acknowledgments

- [Telethon](https://github.com/LonamiWebs/Telethon) - MTProto API client
- [Termux](https://termux.com/) - Android terminal emulator
- [psutil](https://github.com/giampaolo/psutil) - System and process utilities
- Komunitas Telegram Bot Indonesia

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/NgrhDn/Project-Forward-Bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/NgrhDn/Project-Forward-Bot/discussions)
- **Telegram**: [@YourTelegramUsername](https://t.me/YourTelegramUsername)

---

## 🔄 Changelog

### v2.1.0 (Latest)
- ⏸️ **Smart Pause System**: Auto-pause saat memory penuh dengan interactive resume
- 🆔 **Perfect Anti-Duplicate**: Per-message ID tracking yang tidak pernah duplicate
- 📁 **Auto Log Management**: Otomatis setup folder log baru saat ganti source channel
- 🔧 **Memory Monitoring**: Real-time memory monitoring dengan threshold auto-pause
- 🎮 **Interactive Controls**: Pause/resume/quit controls yang responsive
- 💾 **Smart ID Management**: Improved ID tracking dan file handling
- 📊 **Better Progress Display**: Progress dengan memory status real-time
- 🛠️ **Helper Scripts**: setup_channel.py untuk easy channel switching
- 🔄 **Batch Optimization**: Smaller batch size (25) untuk Termux performance

### v2.0.0
- ✨ **AUTO-RECONNECT**: Never stops due to network issues
- 🛡️ **Error Recovery**: Automatic recovery from all network errors
- 📱 **Termux Optimization**: Full Android/Termux support
- ⚡ **Performance**: Faster processing with smart delays
- 🔐 **Wake Lock**: Prevent Android from killing the process
- 📊 **Better Logging**: Comprehensive logging system
- 🎯 **Smart Retry**: Progressive delays for retry attempts

### v1.0.0
- 🎉 Initial release
- ✅ Basic forwarding functionality
- 📁 Log system per channel
- 🔄 Retry mechanism for failed messages

---

**⭐ Jika project ini membantu, berikan star di GitHub!**

**🚀 Ready to use dengan confidence - Bot yang tidak pernah berhenti!**
