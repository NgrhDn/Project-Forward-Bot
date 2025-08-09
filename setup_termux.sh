#!/bin/bash

# --- Script Setup Otomatis untuk Termux ---
# Script ini akan menginstal semua dependensi yang dibutuhkan
# dan menyiapkan environment untuk menjalankan bot.

echo "🚀 Memulai setup untuk Project Forward Bot di Termux..."

# 1. Update & Upgrade package manager Termux
echo "🔄 Mengupdate package list..."
pkg update -y && pkg upgrade -y

# 2. Install dependensi dasar (Python & Git)
echo "🐍 Menginstal Python dan Git..."
pkg install python git -y

# 3. Install dependensi build (diperlukan untuk beberapa paket Python)
echo "🔧 Menginstal build essentials..."
pkg install build-essential libjpeg-turbo libwebp -y

# 4. Install dependensi Python dari requirements.txt
echo "📦 Menginstal paket Python (Telethon & Psutil)..."
pip install -r requirements.txt

# 5. Membuat script helper menjadi executable
echo "chmod +x run_termux.sh"
chmod +x run_termux.sh

echo "✅ Setup selesai!"
echo "Sekarang Anda bisa mengkonfigurasi channel dengan 'python setup_channel.py'"
echo "Dan menjalankan bot dengan './run_termux.sh' atau 'python main.py'"
