from telethon import TelegramClient, events
import asyncio
import os

# === Konfigurasi API ===
api_id = 20472458
api_hash = '633ab23da7659741154c322e894e4d61'

# === ID Channel dan Grup ===
source_channel = -1002740767862  # channel sumber
target_channel = -4985870936     # grup tujuan

# === Inisialisasi Client ===
client = TelegramClient('session_danda', api_id, api_hash)

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

# === Simpan ID ===
def save_forwarded_id(msg_id):
    if msg_id not in forwarded_ids:
        forwarded_ids.add(msg_id)
        with open(forwarded_file, 'a') as f:
            f.write(str(msg_id) + '\n')

def save_failed_id(msg_id):
    if msg_id not in failed_ids:
        failed_ids.add(msg_id)
        with open(failed_file, 'a') as f:
            f.write(str(msg_id) + '\n')

def remove_failed_id(msg_id):
    if msg_id in failed_ids:
        failed_ids.remove(msg_id)
        with open(failed_file, 'w') as f:
            for i in failed_ids:
                f.write(str(i) + '\n')

# === Logging ===
def log_to_file(message, status, note=''):
    with open(log_file, 'a') as f:
        f.write(f"[{status.upper()}] ID: {message.id} | {note}\n")

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

# === Fungsi Kirim Pesan ===
async def check_and_forward(message):
    if message.id in forwarded_ids:
        return 'skip'

    if message.photo or message.video or message.gif:
        try:
            await message.forward_to(target_channel)
            save_forwarded_id(message.id)
            remove_failed_id(message.id)
            return 'sent'
        except Exception as e:
            if "FloodWait" in str(type(e)) or "FloodWait" in str(e):
                delay = int(''.join(filter(str.isdigit, str(e))))
                print(f"⏳ FloodWait terdeteksi. Tunggu {delay} detik...")
                await asyncio.sleep(delay)
                return await check_and_forward(message)  # Retry
            else:
                return 'error'
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
        async for _ in client.iter_messages(source_channel):
            total += 1
        print(f"📦 Total pesan: {total}")
        count = 0
        sent = 0
        async for message in client.iter_messages(source_channel, reverse=True):
            count += 1
            result = await check_and_forward(message)
            if result == 'sent':
                sent += 1
                log_success(message, index=count, total=total)
            elif result == 'skip':
                log_skipped(message, index=count, total=total)
            else:
                log_failed(message, index=count, total=total)
            if count % 100 == 0:
                print("🛑 Delay 60 detik untuk keamanan...")
                await asyncio.sleep(60)
            await asyncio.sleep(1.5)
        print(f"\n🎉 Scan selesai! Media terkirim: {sent} dari {total} pesan.")

    elif pilihan == '2':
        try:
            jumlah = int(input("Jumlah pesan terakhir yang ingin dipindai: "))
        except ValueError:
            print("❌ Input tidak valid.")
            return
        count = 0
        sent = 0
        async for message in client.iter_messages(source_channel, limit=jumlah):
            count += 1
            result = await check_and_forward(message)
            if result == 'sent':
                sent += 1
                log_success(message, index=count, total=jumlah)
            elif result == 'skip':
                log_skipped(message, index=count, total=jumlah)
            else:
                log_failed(message, index=count, total=jumlah)
            if count % 100 == 0:
                print("🛑 Delay 60 detik untuk keamanan...")
                await asyncio.sleep(60)
            await asyncio.sleep(1.5)
        print(f"\n🎉 Selesai! Media terkirim: {sent} dari {jumlah} pesan.")

    elif pilihan == '3':
        print("⚡ Mode realtime aktif...")
    else:
        print("❌ Pilihan tidak dikenali.")

# === Realtime Handler ===
@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    result = await check_and_forward(event.message)
    if result == 'sent':
        log_success(event.message, context='Realtime')

# === Retry Loop ===
async def retry_loop():
    while True:
        if not failed_ids:
            await asyncio.sleep(30)
            continue
        retry_batch = list(failed_ids)[:100]
        print(f"\n🔁 Retry batch {len(retry_batch)} media gagal...")
        for i, msg_id in enumerate(retry_batch, 1):
            try:
                message = await client.get_messages(source_channel, ids=msg_id)
                result = await check_and_forward(message)
                if result == 'sent':
                    log_success(message, context='RETRY')
                elif result == 'skip':
                    log_skipped(message, reason='Sudah sukses sebelumnya')
                else:
                    log_failed(message, reason='Masih gagal saat retry')
            except Exception as e:
                print(f"❌ Gagal ambil ID {msg_id}: {e}")
            await asyncio.sleep(2)
        print("⏳ Delay 60 detik sebelum lanjut batch berikutnya...\n")
        await asyncio.sleep(60)

# === Main Program ===
async def main():
    await scan_old_messages()
    asyncio.create_task(retry_loop())
    print("🤖 Menunggu pesan baru secara realtime...")

client.start()
client.loop.run_until_complete(main())
client.run_until_disconnected()
