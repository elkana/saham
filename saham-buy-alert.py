# TO RUN in virtual env:
# py -m venv venv
# venv\Scripts\activate  # Aktifkan env (di Windows)
# pip install yfinance pandas
# py yfinance.py
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import requests  # Untuk Telegram
from yfinance.exceptions import YFRateLimitError  # Import spesifik untuk handle error

# Konfigurasi
symbol = "PSAB.JK"
alert_price = 210.00  # Threshold rendah untuk buy (dekat 52-week low: 206.00 IDR)
telegram_token = "7677796645:AAEYLZhLLB7lhXFf2Jq7WVdSWi64FxRy4Y4"
chat_id = "133717472"  # Ganti dengan chat ID asli
alert_sent = False
update_interval = 120  # 2 menit (kurangi request untuk hindari rate limit)

# Fungsi kirim Telegram
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Alert berhasil dikirim ke Telegram!")
        else:
            print(f"Error kirim alert: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error koneksi Telegram: {e}")

# Fungsi fetch data dengan error handling
def fetch_stock_data(symbol):
    global alert_sent
    ticker = yf.Ticker(symbol)
    
    try:
        # Prioritas: Gunakan fast_info (ringan, cepat)
        fast_info = ticker.fast_info
        current_price = fast_info.get('lastPrice', fast_info.get('regularMarketPrice', None))
        
        if current_price is None:
            raise ValueError("Tidak bisa ambil harga dari fast_info, coba history...")
        
        # Ambil previous close untuk change
        prev_close = fast_info.get('previousClose', None)
        if prev_close:
            change = current_price - prev_close
            change_pct = (change / prev_close * 100)
        else:
            change = change_pct = None
        
        # Info tambahan (volume dari history ringan)
        hist = ticker.history(period='1d', interval='1d')  # Daily summary
        volume = hist['Volume'].iloc[-1] if not hist.empty else None
        
        # Hitung display values untuk hindari f-string error
        prev_display = f"{prev_close:.2f}" if prev_close is not None else 'N/A'
        volume_display = f"{int(volume):,}" if volume is not None else 'N/A'
        
        print(f"\n=== Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
        print(f"Saham: {symbol}")
        print(f"Harga Terakhir: {current_price:.2f} IDR")
        print(f"Previous Close: {prev_display}")
        if change is not None:
            print(f"Change: {change:.2f} ({change_pct:.2f}%)")
        print(f"Volume: {volume_display}")
        print("=====================================")
        
    except YFRateLimitError:
        print("⚠️ Rate limit Yahoo! Menunggu 5 menit sebelum retry...")
        time.sleep(300)  # Retry delay
        return fetch_stock_data(symbol)  # Recursive retry
    
    except Exception as e:
        print(f"Error fetch data: {e}. Skip update ini, coba lagi nanti.")
        return  # Skip, jangan crash
    
    # Check alert BUY (harga rendah)
    if not alert_sent and current_price <= (alert_price + 0.01):  # Toleransi 0.01 untuk floating point
        alert_message = f"🟢 <b>ALERT BUY SAHAM PSAB.JK</b>\nHarga turun ke {current_price:.2f} IDR (<= {alert_price} IDR)!\nWaktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S WIB')}\n\nPotensi buy low! Cek fundamental & volume sebelum action."
        send_telegram_alert(alert_message)
        alert_sent = True  # Jangan kirim lagi

# Loop monitoring
try:
    print(f"Memulai monitoring {symbol}... Alert buy jika harga <= {alert_price} IDR.")
    print(f"Update setiap {update_interval//60} menit. Hentikan dengan Ctrl+C.")
    while True:
        fetch_stock_data(symbol)
        time.sleep(update_interval)
except KeyboardInterrupt:
    print("\nMonitoring dihentikan.")