@echo off
REM --- Script Batch untuk Menjalankan Bot dengan Auto-Restart di Windows ---

title Project Forward Bot Runner

:start
echo.
echo [INFO] 🚀 Memulai Project Forward Bot...
echo [INFO] 📝 Log akan disimpan di folder logs/ dan file bot.log
echo [INFO] 💡 Untuk menghentikan bot sepenuhnya, tutup jendela ini atau tekan Ctrl+C.
echo.

REM Jalankan bot utama menggunakan skrip Python auto-restart
python run_bot.py

REM Cek error level. Jika bot berhenti karena error, akan ada jeda sebelum restart.
REM run_bot.py sudah menangani loop, jadi bagian ini mungkin hanya sebagai fallback.
echo.
echo [WARNING] ⚠️ Script utama telah berhenti. Merestart dalam 15 detik...
echo [INFO] Tutup jendela ini untuk menghentikan proses restart.
timeout /t 15 /nobreak

goto start
