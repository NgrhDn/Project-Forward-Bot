#!/bin/bash

# --- Script untuk Menjalankan Bot dengan Auto-Restart di Termux ---
# Script ini akan menjaga bot tetap berjalan. Jika bot berhenti karena
# error tak terduga (selain Ctrl+C), script akan otomatis merestart bot.

# Mengaktifkan wake lock untuk mencegah Termux/Android masuk deep sleep
termux-wake-lock

echo "🔒 Termux Wake Lock diaktifkan. Mencegah HP dari deep sleep."
echo "🚀 Memulai Project Forward Bot..."
echo "📝 Log akan disimpan di folder logs/ dan file bot.log"
echo "💡 Untuk menghentikan bot sepenuhnya, tekan Ctrl+C"

# Loop tak terbatas untuk auto-restart
while true; do
    # Jalankan bot utama menggunakan Python
    python main.py

    # Cek exit code dari script python.
    # Jika exit code bukan 0 (error), tunggu sebentar lalu restart.
    # Jika exit code 0 (berhenti normal, misal via Ctrl+C), maka keluar dari loop.
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "🛑 Bot dihentikan secara normal. Keluar dari script."
        break
    else
        echo "⚠️ Bot berhenti dengan error (exit code: $exit_code). Merestart dalam 10 detik..."
        sleep 10
    fi
done

# Melepas wake lock saat script dihentikan
termux-wake-unlock
echo "🔓 Termux Wake Lock dilepaskan."
