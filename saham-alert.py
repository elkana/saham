# TO RUN in virtual env:
# py -m venv venv
# venv\Scripts\activate  # Aktifkan env (di Windows)
# pip install yfinance pandas
# py yfinance.py
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import requests  # Untuk kirim ke Telegram

# Konfigurasi
symbol = "PSAB.JK"
alert_price = 620.00  # Harga target untuk alert
telegram_token = "7677796645:AAEYLZhLLB7lhXFf2Jq7WVdSWi64FxRy4Y4"  # Token bot-mu
chat_id = "133717472"  # Ganti dengan chat ID asli (misalnya: 123456789 atau -123456789 untuk group)
alert_sent = False  # Flag untuk kirim alert sekali saja

# Fungsi kirim pesan ke Telegram
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"  # Optional: untuk format bold/italic
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Alert berhasil dikirim ke Telegram!")
        else:
            print(f"Error kirim alert: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error koneksi Telegram: {e}")

# Fungsi untuk fetch data intraday
def fetch_stock_data(symbol, interval='1m', period='1d'):
    global alert_sent
    ticker = yf.Ticker(symbol)
    
    # Ambil data historis intraday
    data = ticker.history(period=period, interval=interval)
    
    if data.empty:
        print("Tidak ada data tersedia (pasar tutup?).")
        return
    
    # Ambil bar terakhir
    latest = data.iloc[-1]
    fast_info = ticker.fast_info
    
    current_price = latest['Close']
    
    print(f"\n=== Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"Saham: {symbol}")
    print(f"Harga Terakhir: {current_price:.2f} IDR")
    print(f"Open: {latest['Open']:.2f} | High: {latest['High']:.2f} | Low: {latest['Low']:.2f}")
    print(f"Volume: {latest['Volume']:,}")
    if len(data) > 1:
        prev_close = data.iloc[-2]['Close']
        change = current_price - prev_close
        change_pct = (change / prev_close * 100)
        print(f"Change: {change:.2f} ({change_pct:.2f}%)")
    print(f"Previous Close: {fast_info.get('previousClose', 'N/A')}")
    print("=====================================")
    
    # Check alert
    if not alert_sent and current_price >= (alert_price - 0.01):  # Toleransi 0.01 untuk floating point
        alert_message = f"🚨 <b>ALERT SAHAM PSAB.JK</b>\nHarga mencapai {current_price:.2f} IDR (>= {alert_price} IDR)!\nWaktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S WIB')}\n\nCek app trading-mu segera!"
        send_telegram_alert(alert_message)
        alert_sent = True  # Jangan kirim lagi

# Loop untuk update (setiap 1 menit)
try:
    print(f"Memulai monitoring {symbol}... Alert akan dikirim jika harga >= {alert_price} IDR.")
    print("Hentikan dengan Ctrl+C.")
    while True:
        fetch_stock_data(symbol)
        time.sleep(60)  # Update setiap 1 menit
except KeyboardInterrupt:
    print("\nMonitoring dihentikan oleh user.")