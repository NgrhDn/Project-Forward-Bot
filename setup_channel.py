import os
import re
import shutil

MAIN_PY_FILE = 'main.py'
LOGS_DIR = 'logs'
BACKUP_DIR = 'logs_backup'

def get_user_input(prompt):
    """Meminta input dari user dan memastikan tidak kosong."""
    while True:
        try:
            value = input(prompt).strip()
            if value:
                return int(value)
            else:
                print("❌ Input tidak boleh kosong. Silakan coba lagi.")
        except ValueError:
            print("❌ Input harus berupa angka (ID channel). Silakan coba lagi.")
        except (KeyboardInterrupt, EOFError):
            print("\n🛑 Proses dibatalkan.")
            exit()

def update_main_py(source_id, target_id):
    """Mengupdate file main.py dengan ID channel yang baru."""
    try:
        with open(MAIN_PY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        # Ganti source_channel
        content = re.sub(r"source_channel\s*=\s*-?\d+", f"source_channel = {source_id}", content)
        
        # Ganti target_channel
        content = re.sub(r"target_channel\s*=\s*-?\d+", f"target_channel = {target_id}", content)

        with open(MAIN_PY_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ File '{MAIN_PY_FILE}' berhasil diupdate.")
        return True
    except FileNotFoundError:
        print(f"❌ Error: File '{MAIN_PY_FILE}' tidak ditemukan.")
        return False
    except Exception as e:
        print(f"❌ Gagal mengupdate file '{MAIN_PY_FILE}': {e}")
        return False

def manage_log_directory(old_source_id, new_source_id):
    """Mengelola direktori log, membackup yang lama dan membuat yang baru."""
    old_log_path = os.path.join(LOGS_DIR, str(old_source_id))
    new_log_path = os.path.join(LOGS_DIR, str(new_source_id))

    # 1. Backup direktori log lama jika ada
    if os.path.isdir(old_log_path):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        backup_target = os.path.join(BACKUP_DIR, f"{old_source_id}_{os.path.basename(os.path.normpath(old_log_path))}")
        
        # Jika backup dengan nama yang sama sudah ada, tambahkan timestamp
        if os.path.exists(backup_target):
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_target = f"{backup_target}_{timestamp}"

        try:
            shutil.move(old_log_path, backup_target)
            print(f"📦 Log lama dari channel '{old_source_id}' telah dibackup ke '{backup_target}'")
        except Exception as e:
            print(f"⚠️ Gagal membackup log lama: {e}")

    # 2. Buat direktori log baru jika belum ada
    if not os.path.isdir(new_log_path):
        os.makedirs(new_log_path, exist_ok=True)
        print(f"📁 Direktori log baru dibuat di '{new_log_path}'")

def get_current_ids():
    """Mendapatkan ID channel saat ini dari main.py."""
    try:
        with open(MAIN_PY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        source_match = re.search(r"source_channel\s*=\s*(-?\d+)", content)
        target_match = re.search(r"target_channel\s*=\s*(-?\d+)", content)

        if source_match and target_match:
            return int(source_match.group(1)), int(target_match.group(1))
        else:
            print("⚠️ Tidak dapat menemukan ID channel saat ini di main.py. Akan menggunakan nilai default.")
            return 0, 0
    except FileNotFoundError:
        print(f"❌ Error: File '{MAIN_PY_FILE}' tidak ditemukan.")
        exit()
    except Exception as e:
        print(f"❌ Gagal membaca ID saat ini: {e}")
        exit()

def main():
    """Fungsi utama untuk menjalankan script setup."""
    print("--- 🔧 Setup Konfigurasi Channel Bot ---")
    print("Script ini akan membantu Anda mengganti channel sumber dan tujuan.")
    print("Log dari channel lama akan otomatis di-backup.")
    print("Tekan Ctrl+C untuk membatalkan kapan saja.\n")

    current_source, current_target = get_current_ids()
    print(f"ℹ️  Channel saat ini: Sumber = {current_source}, Tujuan = {current_target}\n")

    new_source = get_user_input("Masukkan ID Channel Sumber Baru: ")
    new_target = get_user_input("Masukkan ID Grup/Channel Tujuan Baru: ")

    print("\n--- Ringkasan Perubahan ---")
    print(f"Sumber Lama: {current_source} -> Sumber Baru: {new_source}")
    print(f"Tujuan Lama: {current_target} -> Tujuan Baru: {new_target}")
    
    confirm = input("\nApakah Anda yakin ingin melanjutkan? (y/n): ").lower()
    
    if confirm == 'y':
        print("\n🚀 Memproses perubahan...")
        if update_main_py(new_source, new_target):
            manage_log_directory(current_source, new_source)
            print("\n✅ Konfigurasi berhasil diubah!")
            print("Bot sekarang siap dijalankan dengan 'python main.py' atau './run_termux.sh'")
        else:
            print("\n❌ Gagal menerapkan perubahan. Mohon periksa error di atas.")
    else:
        print("\n🛑 Perubahan dibatalkan.")

if __name__ == "__main__":
    main()
