from telethon import TelegramClient, events
from telethon.errors import ConnectionError, FloodWaitError, AuthKeyDuplicatedError, RPCError
import asyncio
import os
import time
import logging
import signal
import sys

# === Konfigurasi API ===
api_id = 20472458
api_hash = '633ab23da7659741154c322e894e4d61'

# === ID Channel dan Grup ===
source_channel = -1002740767862  # channel sumber
target_channel = -4985870936     # grup tujuan

# === Inisialisasi Client ===
client = TelegramClient('session_danda', api_id, api_hash)

# === Setup Logging ===
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

# === Variabel Global untuk Status Koneksi ===
is_connected = False
reconnect_attempts = 0
max_reconnect_delay = 180  # 3 menit maksimal delay untuk Termux
should_stop = False
is_paused = False
pause_reason = ""

# === Struktur Folder Log Berdasarkan Channel Sumber ===
log_dir = f'logs/{source_channel}'
os.makedirs(log_dir, exist_ok=True)

forwarded_file = os.path.join(log_dir, 'forwarded_ids.txt')
failed_file = os.path.join(log_dir, 'failed_ids.txt')
log_file = os.path.join(log_dir, 'log.txt')

forwarded_ids = set()
failed_ids = set()

# === Load Forwarded IDs ===
if os.path.exists(forwarded_file):
    with open(forwarded_file, 'r') as f:
        forwarded_ids = set(int(line.strip()) for line in f if line.strip().isdigit())

# === Load Failed IDs ===
if os.path.exists(failed_file):
    with open(failed_file, 'r') as f:
        failed_ids = set(int(line.strip()) for line in f if line.strip().isdigit())

# === Memory & System Monitoring ===
def check_memory_usage():
    """Check memory usage dan return status"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        available_mb = memory.available / (1024 * 1024)
        used_percent = memory.percent
        
        # Ambang batas: kurang dari 100MB available atau lebih dari 90% used
        if available_mb < 100 or used_percent > 90:
            return False, f"Memory rendah: {available_mb:.0f}MB tersisa ({used_percent:.1f}% used)"
        return True, f"Memory OK: {available_mb:.0f}MB tersisa ({used_percent:.1f}% used)"
    except ImportError:
        # Jika psutil tidak tersedia, gunakan fallback
        try:
            # Untuk Android/Termux, cek /proc/meminfo
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            mem_total = int([x for x in meminfo.split('\n') if 'MemTotal' in x][0].split()[1])
            mem_available = int([x for x in meminfo.split('\n') if 'MemAvailable' in x][0].split()[1])
            
            available_mb = mem_available / 1024
            used_percent = ((mem_total - mem_available) / mem_total) * 100
            
            if available_mb < 100 or used_percent > 90:
                return False, f"Memory rendah: {available_mb:.0f}MB tersisa ({used_percent:.1f}% used)"
            return True, f"Memory OK: {available_mb:.0f}MB tersisa ({used_percent:.1f}% used)"
        except:
            return True, "Memory check tidak tersedia"

def pause_bot(reason):
    """Pause bot dengan alasan tertentu"""
    global is_paused, pause_reason
    is_paused = True
    pause_reason = reason
    print(f"\n⏸️ BOT DIJEDA: {reason}")
    print("🔧 Silakan bersihkan memory/storage atau perbaiki masalah")
    print("⚡ Ketik 'c' + Enter untuk melanjutkan setelah masalah diperbaiki")

async def wait_for_resume():
    """Tunggu user untuk melanjutkan bot"""
    global is_paused, should_stop
    
    while is_paused and not should_stop:
        print(f"\n⏸️ Bot dijeda: {pause_reason}")
        print("💡 Pilihan:")
        print("   c = Continue (lanjutkan)")
        print("   q = Quit (keluar)")
        print("   m = Check memory status")
        
        try:
            choice = input("Pilihan (c/q/m): ").strip().lower()
            
            if choice == 'c':
                # Cek memory lagi sebelum lanjut
                memory_ok, memory_status = check_memory_usage()
                print(f"📊 {memory_status}")
                
                if memory_ok:
                    is_paused = False
                    print("✅ Bot dilanjutkan!")
                    break
                else:
                    print("❌ Memory masih bermasalah. Bersihkan dulu sebelum lanjut.")
                    
            elif choice == 'q':
                should_stop = True
                is_paused = False
                print("🛑 Bot akan berhenti...")
                break
                
            elif choice == 'm':
                memory_ok, memory_status = check_memory_usage()
                print(f"📊 {memory_status}")
                
            else:
                print("❌ Pilihan tidak valid. Gunakan c/q/m")
                
        except KeyboardInterrupt:
            should_stop = True
            is_paused = False
            break
        except:
            print("❌ Error input. Coba lagi...")
            await asyncio.sleep(1)

# === Simpan ID ===
def save_forwarded_id(msg_id):
    """Simpan ID pesan yang sudah berhasil dikirim"""
    if msg_id not in forwarded_ids:
        forwarded_ids.add(msg_id)
        with open(forwarded_file, 'a', encoding='utf-8') as f:
            f.write(str(msg_id) + '\n')
        print(f"💾 Saved forwarded ID: {msg_id}")

def save_failed_id(msg_id):
    """Simpan ID pesan yang gagal dikirim"""
    if msg_id not in failed_ids:
        failed_ids.add(msg_id)
        with open(failed_file, 'a', encoding='utf-8') as f:
            f.write(str(msg_id) + '\n')
        print(f"💾 Saved failed ID: {msg_id}")

def remove_failed_id(msg_id):
    """Hapus ID dari daftar gagal ketika berhasil dikirim"""
    if msg_id in failed_ids:
        failed_ids.remove(msg_id)
        with open(failed_file, 'w', encoding='utf-8') as f:
            for i in failed_ids:
                f.write(str(i) + '\n')
        print(f"🗑️ Removed from failed list: {msg_id}")

def is_message_already_forwarded(msg_id):
    """Cek apakah pesan sudah pernah dikirim"""
    return msg_id in forwarded_ids

def get_unique_message_id(message):
    """Generate unique ID untuk setiap pesan individual"""
    # Gunakan message.id sebagai unique identifier
    # Setiap pesan di Telegram memiliki ID unik per channel
    return message.id

# === Fungsi Reconnect ===
async def ensure_connection():
    global is_connected, reconnect_attempts, should_stop
    
    while not is_connected and not should_stop:
        try:
            print(f"🔄 Mencoba koneksi ke Telegram... (Percobaan ke-{reconnect_attempts + 1})")
            
            if client.is_connected():
                await client.disconnect()
                await asyncio.sleep(2)  # Brief delay untuk Termux
            
            await client.connect()
            
            # Test koneksi dengan request sederhana
            me = await client.get_me()
            print(f"👤 Logged in as: {me.first_name}")
            
            is_connected = True
            reconnect_attempts = 0
            print("✅ Koneksi berhasil!")
            return True
            
        except Exception as e:
            reconnect_attempts += 1
            # Delay lebih pendek untuk Termux (network mobile lebih tidak stabil)
            delay = min(15 + (reconnect_attempts * 5), max_reconnect_delay)
            print(f"❌ Koneksi gagal: {e}")
            print(f"⏳ Mencoba lagi dalam {delay} detik...")
            
            # Bagi delay menjadi chunks untuk bisa respond ke interrupt
            for i in range(delay):
                if should_stop:
                    return False
                await asyncio.sleep(1)
                if i % 10 == 0 and i > 0:
                    print(f"⏳ {delay - i} detik lagi...")
    
    return not should_stop

async def safe_request(func, *args, max_retries=3, **kwargs):
    """Wrapper untuk request yang aman dengan auto-reconnect (optimized untuk Termux)"""
    global is_connected, should_stop
    
    for attempt in range(max_retries):
        if should_stop:
            return None
            
        try:
            if not is_connected:
                success = await ensure_connection()
                if not success:
                    return None
            
            return await func(*args, **kwargs)
            
        except (ConnectionError, OSError, RPCError) as e:
            print(f"⚠️ Koneksi terputus: {e}")
            is_connected = False
            
            if attempt < max_retries - 1:
                print(f"🔄 Mencoba reconnect... ({attempt + 1}/{max_retries})")
                success = await ensure_connection()
                if not success:
                    return None
            else:
                print(f"❌ Gagal setelah {max_retries} percobaan")
                raise
                
        except FloodWaitError as e:
            wait_time = min(e.seconds, 300)  # Max 5 menit untuk FloodWait
            print(f"⏳ FloodWait: Tunggu {wait_time} detik...")
            for i in range(wait_time):
                if should_stop:
                    return None
                await asyncio.sleep(1)
                if i % 30 == 0 and i > 0:
                    print(f"⏳ FloodWait: {wait_time - i} detik lagi...")
            
        except Exception as e:
            print(f"❌ Error tidak terduga: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(3)  # Delay lebih pendek untuk Termux
            else:
                raise
    
    return None
# === Signal Handler untuk Termux ===
def signal_handler(signum, frame):
    global should_stop
    print(f"\n🛑 Received signal {signum}")
    print("🔄 Gracefully shutting down...")
    should_stop = True

# Setup signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# === Logging ===
def log_to_file(message, status, note=''):
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] [{status.upper()}] ID: {message.id} | {note}\n")
    except Exception as e:
        print(f"❌ Error writing to log file: {e}")

def log_success(message, context='Scan', index=None, total=None):
    prefix = f"[{index} dari {total}] " if index and total else ''
    print(f"{prefix}✅ Dikirim (ID: {message.id}) {'📥 ' + context}")
    log_to_file(message, 'success', context)

def log_failed(message, reason='', index=None, total=None):
    prefix = f"[{index} dari {total}] " if index and total else ''
    print(f"{prefix}❌ Gagal kirim ID {message.id} {reason}")
    save_failed_id(message.id)
    log_to_file(message, 'failed', reason)

def log_skipped(message, reason='', index=None, total=None):
    prefix = f"[{index} dari {total}] " if index and total else ''
    print(f"{prefix}♻️ Lewat (ID: {message.id}) {reason}")
    log_to_file(message, 'skipped', reason)

# === Fungsi Kirim Pesan ===
async def check_and_forward(message):
    global is_paused, should_stop
    
    # Cek apakah bot sedang di-pause
    if is_paused:
        await wait_for_resume()
        if should_stop:
            return 'stopped'
    
    # Generate unique ID untuk pesan ini
    unique_id = get_unique_message_id(message)
    
    # Cek apakah sudah pernah dikirim (anti-duplicate)
    if is_message_already_forwarded(unique_id):
        return 'skip'

    # Cek apakah pesan mengandung media (foto, video, GIF)
    if message.photo or message.video or message.gif or message.document:
        try:
            # Cek memory sebelum forward
            memory_ok, memory_status = check_memory_usage()
            if not memory_ok:
                pause_bot(f"Memory penuh - {memory_status}")
                await wait_for_resume()
                if should_stop:
                    return 'stopped'
            
            # Forward pesan ke target channel
            await safe_request(message.forward_to, target_channel)
            
            # Simpan sebagai berhasil
            save_forwarded_id(unique_id)
            remove_failed_id(unique_id)
            
            print(f"📤 Media berhasil dikirim - ID: {unique_id}")
            return 'sent'
            
        except FloodWaitError as e:
            wait_time = min(e.seconds, 300)  # Max 5 menit untuk FloodWait
            print(f"⏳ FloodWait terdeteksi. Tunggu {wait_time} detik...")
            
            # Pause bot sementara karena FloodWait
            pause_bot(f"FloodWait {wait_time} detik")
            
            # Tunggu FloodWait selesai
            for i in range(wait_time):
                if should_stop:
                    return 'stopped'
                await asyncio.sleep(1)
                if (i + 1) % 30 == 0:
                    print(f"⏳ FloodWait: {wait_time - i - 1} detik lagi...")
            
            is_paused = False  # Resume setelah FloodWait
            return await check_and_forward(message)  # Retry
            
        except Exception as e:
            print(f"❌ Error saat forward ID {unique_id}: {e}")
            save_failed_id(unique_id)
            return 'error'
    
    # Bukan media, skip
    return 'skip'

# === Pemindaian Lama ===
async def scan_old_messages():
    print("\n=== Opsi Pemindaian Pesan Lama ===")
    print("1. 📂 Scan semua pesan dari awal")
    print("2. 🔢 Scan sejumlah pesan terakhir")
    print("3. ⚡ Langsung realtime")
    pilihan = input("Pilih opsi (1/2/3): ")

    if pilihan == '1':
        total = 0
        print("📊 Menghitung total pesan...")
        total_count = await safe_request(client.get_messages, source_channel, limit=1)
        if total_count:
            total = total_count[0].id
        print(f"📦 Estimasi total pesan: {total}")
        
        count = 0
        sent = 0
        
        async def process_messages():
            nonlocal count, sent
            try:
                async for message in client.iter_messages(source_channel, reverse=True):
                    if should_stop:
                        print("🛑 Stopping scan due to user request...")
                        break
                    
                    # Cek pause status
                    if is_paused:
                        await wait_for_resume()
                        if should_stop:
                            break
                        
                    count += 1
                    result = await check_and_forward(message)
                    
                    if result == 'stopped':
                        print("🛑 Scan dihentikan...")
                        break
                    elif result == 'sent':
                        sent += 1
                        log_success(message, index=count, total=total)
                    elif result == 'skip':
                        log_skipped(message, "Sudah pernah dikirim", index=count, total=total)
                    else:
                        log_failed(message, "Error saat forward", index=count, total=total)
                    
                    # Delay dan monitoring setiap 25 pesan untuk Termux
                    if count % 25 == 0:
                        memory_ok, memory_status = check_memory_usage()
                        print(f"📊 Progress: {count}/{total} | {memory_status}")
                        
                        if not memory_ok:
                            pause_bot(f"Memory check - {memory_status}")
                            await wait_for_resume()
                            if should_stop:
                                break
                        
                        print("🛑 Delay 20 detik untuk keamanan (per 25 pesan)...")
                        for i in range(20):
                            if should_stop or is_paused:
                                break
                            await asyncio.sleep(1)
                    
                    await asyncio.sleep(1)  # Delay antar pesan
            except Exception as e:
                print(f"❌ Error during message processing: {e}")
                if not should_stop:
                    await asyncio.sleep(5)
        
        await safe_request(process_messages)
        print(f"\n🎉 Scan selesai! Media terkirim: {sent} dari {count} pesan.")

    elif pilihan == '2':
        try:
            jumlah = int(input("Jumlah pesan terakhir yang ingin dipindai: "))
        except ValueError:
            print("❌ Input tidak valid.")
            return
        count = 0
        sent = 0
        
        async def process_limited_messages():
            nonlocal count, sent
            try:
                async for message in client.iter_messages(source_channel, limit=jumlah):
                    if should_stop:
                        print("🛑 Stopping scan due to user request...")
                        break
                    
                    # Cek pause status
                    if is_paused:
                        await wait_for_resume()
                        if should_stop:
                            break
                        
                    count += 1
                    result = await check_and_forward(message)
                    
                    if result == 'stopped':
                        print("🛑 Scan dihentikan...")
                        break
                    elif result == 'sent':
                        sent += 1
                        log_success(message, index=count, total=jumlah)
                    elif result == 'skip':
                        log_skipped(message, "Sudah pernah dikirim", index=count, total=jumlah)
                    else:
                        log_failed(message, "Error saat forward", index=count, total=jumlah)
                    
                    # Delay dan monitoring setiap 25 pesan untuk Termux
                    if count % 25 == 0:
                        memory_ok, memory_status = check_memory_usage()
                        print(f"📊 Progress: {count}/{jumlah} | {memory_status}")
                        
                        if not memory_ok:
                            pause_bot(f"Memory check - {memory_status}")
                            await wait_for_resume()
                            if should_stop:
                                break
                        
                        print("🛑 Delay 20 detik untuk keamanan (per 25 pesan)...")
                        for i in range(20):
                            if should_stop or is_paused:
                                break
                            await asyncio.sleep(1)
                    
                    await asyncio.sleep(1)  # Delay antar pesan
            except Exception as e:
                print(f"❌ Error during message processing: {e}")
                if not should_stop:
                    await asyncio.sleep(5)
        
        await safe_request(process_limited_messages)
        print(f"\n🎉 Selesai! Media terkirim: {sent} dari {jumlah} pesan.")

    elif pilihan == '3':
        print("⚡ Mode realtime aktif...")
    else:
        print("❌ Pilihan tidak dikenali.")

# === Realtime Handler ===
@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    global is_paused, should_stop
    
    # Skip jika bot sedang di-pause atau dihentikan
    if is_paused or should_stop:
        return
        
    result = await check_and_forward(event.message)
    if result == 'sent':
        log_success(event.message, context='Realtime')
    elif result == 'skip':
        print(f"♻️ Realtime skip (ID: {event.message.id}) - Sudah pernah dikirim")
    elif result == 'stopped':
        print("🛑 Realtime handler stopped")
    elif result == 'error':
        print(f"❌ Realtime error (ID: {event.message.id})")

# === Retry Loop ===
async def retry_loop():
    global should_stop, is_paused
    
    while not should_stop:
        try:
            # Skip jika bot di-pause
            if is_paused:
                await asyncio.sleep(5)
                continue
                
            if not failed_ids:
                for i in range(30):  # 30 detik delay
                    if should_stop or is_paused:
                        return
                    await asyncio.sleep(1)
                continue
            
            # Cek memory sebelum retry
            memory_ok, memory_status = check_memory_usage()
            if not memory_ok:
                pause_bot(f"Memory check saat retry - {memory_status}")
                await wait_for_resume()
                if should_stop:
                    return
                continue
            
            retry_batch = list(failed_ids)[:25]  # Batch lebih kecil untuk Termux
            print(f"\n🔁 Retry batch {len(retry_batch)} media gagal...")
            print(f"📊 {memory_status}")
            
            for i, msg_id in enumerate(retry_batch, 1):
                if should_stop or is_paused:
                    return
                    
                try:
                    message = await safe_request(client.get_messages, source_channel, ids=msg_id)
                    if message:
                        result = await check_and_forward(message)
                        if result == 'sent':
                            log_success(message, context='RETRY')
                        elif result == 'skip':
                            log_skipped(message, reason='Sudah sukses sebelumnya')
                        elif result == 'stopped':
                            return
                        else:
                            log_failed(message, reason='Masih gagal saat retry')
                except Exception as e:
                    print(f"❌ Gagal ambil ID {msg_id}: {e}")
                
                await asyncio.sleep(1)  # Delay antar retry
            
            print("⏳ Delay 30 detik sebelum lanjut batch berikutnya...\n")
            for i in range(30):
                if should_stop or is_paused:
                    return
                await asyncio.sleep(1)
            
        except Exception as e:
            print(f"❌ Error dalam retry loop: {e}")
            for i in range(15):  # 15 detik delay saat error
                if should_stop or is_paused:
                    return
                await asyncio.sleep(1)

# === Main Program ===
async def main():
    global is_connected, should_stop
    
    print("🚀 Memulai bot dengan auto-reconnect (Termux Edition)...")
    print("📱 Optimized untuk Android/Termux environment")
    
    # Pastikan koneksi pertama kali
    success = await ensure_connection()
    if not success:
        print("❌ Gagal koneksi awal, keluar...")
        return
    
    # Jalankan scanning
    await scan_old_messages()
    
    if should_stop:
        print("🛑 Bot dihentikan sebelum realtime mode")
        return
    
    # Start retry loop sebagai background task
    retry_task = asyncio.create_task(retry_loop())
    
    print("🤖 Menunggu pesan baru secara realtime...")
    print("📡 Bot akan terus mencoba reconnect jika koneksi terputus")
    print("⏹️ Tekan Ctrl+C untuk menghentikan bot")
    print("📱 Jaga Termux tetap aktif untuk performa optimal")
    
    # Keep alive loop dengan connection monitoring
    try:
        while not should_stop:
            if not is_connected:
                success = await ensure_connection()
                if not success:
                    break
            
            # Check connection setiap 20 detik (lebih sering untuk mobile)
            for i in range(20):
                if should_stop:
                    break
                await asyncio.sleep(1)
                
    except KeyboardInterrupt:
        print("\n🛑 Bot dihentikan oleh user")
    finally:
        should_stop = True
        retry_task.cancel()
        try:
            await retry_task
        except asyncio.CancelledError:
            pass

# === Connection Monitor ===
async def connection_monitor():
    """Monitor koneksi dan reconnect jika perlu (optimized untuk Termux)"""
    global is_connected, should_stop
    
    while not should_stop:
        try:
            if client.is_connected():
                # Test koneksi dengan ping (lebih ringan untuk mobile)
                try:
                    await asyncio.wait_for(client.get_me(), timeout=10)
                    if not is_connected:
                        is_connected = True
                        print("✅ Koneksi pulih!")
                except asyncio.TimeoutError:
                    print("⚠️ Timeout saat test koneksi")
                    is_connected = False
            else:
                if is_connected:
                    print("⚠️ Koneksi terputus, mencoba reconnect...")
                    is_connected = False
                await ensure_connection()
        except Exception as e:
            if is_connected:
                print(f"⚠️ Masalah koneksi terdeteksi: {e}")
                is_connected = False
        
        # Check lebih sering untuk mobile network
        for i in range(20):
            if should_stop:
                return
            await asyncio.sleep(1)

# === Termux Optimized Startup ===
async def termux_startup():
    """Startup optimized untuk Termux"""
    print("📱 Termux startup sequence...")
    
    # Check network connectivity
    try:
        await asyncio.wait_for(client.connect(), timeout=30)
        print("✅ Network connectivity OK")
    except asyncio.TimeoutError:
        print("❌ Network timeout - check your internet connection")
        return False
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False
    
    return True

try:
    print("🔗 Memulai koneksi awal (Termux Edition)...")
    print("📱 Android/Termux optimizations enabled")
    
    # Termux startup check
    if not asyncio.run(termux_startup()):
        print("❌ Termux startup failed")
        sys.exit(1)
    
    client.start()
    
    # Start connection monitor sebagai background task
    monitor_task = asyncio.create_task(connection_monitor())
    
    # Run main program
    try:
        client.loop.run_until_complete(main())
    finally:
        should_stop = True
        monitor_task.cancel()
        try:
            # Wait for monitor task to finish
            client.loop.run_until_complete(asyncio.gather(monitor_task, return_exceptions=True))
        except:
            pass
    
except KeyboardInterrupt:
    print("\n🛑 Program dihentikan oleh user")
    should_stop = True
except Exception as e:
    print(f"❌ Error fatal: {e}")
    print("🔄 Program akan restart otomatis...")
finally:
    should_stop = True
    try:
        if client.is_connected():
            client.disconnect()
    except:
        pass
    print("👋 Bot stopped")
