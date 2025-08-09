import subprocess
import time
import sys

# --- Script Auto-Restart Berbasis Python ---
# Cocok untuk Windows atau environment di mana shell script tidak ideal.

FILENAME = 'main.py'
PYTHON_EXECUTABLE = sys.executable # Menggunakan interpreter python yang sama untuk menjalankan script

def run_bot():
    """Menjalankan bot dan menangani restart."""
    while True:
        try:
            print(f"🚀 Memulai bot dari file '{FILENAME}'...")
            # Jalankan main.py sebagai proses terpisah
            process = subprocess.Popen([PYTHON_EXECUTABLE, FILENAME])
            
            # Tunggu hingga proses selesai
            process.wait()

            # Jika proses berhenti dengan sengaja (misal, dari dalam script),
            # kita bisa hentikan loop. Di sini kita asumsikan semua pemberhentian
            # butuh restart, kecuali KeyboardInterrupt.
            if process.returncode == 0:
                print("🛑 Bot berhenti secara normal. Script restart selesai.")
                break
            else:
                print(f"⚠️ Bot berhenti dengan kode error: {process.returncode}. Merestart dalam 10 detik...")

        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt diterima. Menghentikan auto-restart.")
            # Pastikan proses anak juga berhenti
            if 'process' in locals() and process.poll() is None:
                process.terminate()
            break
        except Exception as e:
            print(f"❌ Terjadi error pada script restart: {e}")
            print("Merestart dalam 10 detik...")

        time.sleep(10)

if __name__ == "__main__":
    run_bot()
