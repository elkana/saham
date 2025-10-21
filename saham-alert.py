# TO RUN in virtual env:
# py -m venv venv
# venv\Scripts\activate  # Aktifkan env (di Windows)
# pip install yfinance pandas
# python saham-alert.py --code PSAB.JK --mode buy --price 620.00 --telegram-token 7677796645:AAEYLZhLLB7lhXFf2Jq7WVdSWi64FxRy4Y4 --chat-id 133717472
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import requests
from yfinance.exceptions import YFRateLimitError
import argparse

# Parse argumen CLI
parser = argparse.ArgumentParser(description="Saham Alert: Monitor saham IDX dengan Telegram Alert")
parser.add_argument("--code", default="PSAB.JK", help="Kode saham (default: PSAB.JK)")
parser.add_argument("--mode", choices=["sell", "buy"], default="sell", help="Mode alert: sell (harga tinggi) atau buy (harga rendah)")
parser.add_argument("--price", type=float, default=620.00, help="Harga threshold untuk alert (default 620 untuk sell, 210 untuk buy)")
parser.add_argument("--telegram-token", required=True, help="Telegram bot token (wajib)")
parser.add_argument("--chat-id", required=True, help="Telegram chat ID (wajib)")
parser.add_argument("--interval", type=int, default=300, help="Interval update dalam detik (default: 300/5 menit, min 60)")

args = parser.parse_args()

# Validasi interval
if args.interval < 60:
    parser.error("--interval harus minimal 60 detik untuk hindari rate limit.")
    
# Konfigurasi
symbol = args.code.upper()
alert_price = args.price
telegram_token = args.telegram_token
chat_id = args.chat_id
alert_sent = False
update_interval = args.interval

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

# Fungsi fetch data
def fetch_stock_data(symbol):
    global alert_sent
    ticker = yf.Ticker(symbol)
    
    try:
        fast_info = ticker.fast_info
        current_price = fast_info.get('lastPrice', fast_info.get('regularMarketPrice', None))
        
        if current_price is None:
            raise ValueError("Tidak bisa ambil harga dari fast_info")
        
        prev_close = fast_info.get('previousClose', None)
        if prev_close:
            change = current_price - prev_close
            change_pct = (change / prev_close * 100)
        else:
            change = change_pct = None
        
        hist = ticker.history(period='1d', interval='1d')
        volume = hist['Volume'].iloc[-1] if not hist.empty else None
        
        prev_display = f"{prev_close:.2f}" if prev_close is not None else 'N/A'
        volume_display = f"{int(volume):,}" if volume is not None else 'N/A'
        
        print(f"\n=== Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ({args.mode.upper()}) ===")
        print(f"Saham: {symbol}")
        print(f"Harga Terakhir: {current_price:.2f} IDR")
        print(f"Previous Close: {prev_display}")
        if change is not None:
            print(f"Change: {change:.2f} ({change_pct:.2f}%)")
        print(f"Volume: {volume_display}")
        print("=====================================")
        
    except YFRateLimitError:
        print("⚠️ Rate limit Yahoo! Menunggu 5 menit sebelum retry...")
        time.sleep(300)
        return fetch_stock_data(symbol)
    
    except Exception as e:
        print(f"Error fetch data: {e}. Skip update ini.")
        return
    
    # Check alert berdasarkan mode
    condition_met = False
    if args.mode == "sell" and current_price >= (alert_price - 0.01):
        condition_met = True
        emoji = "🔴"
        title = "ALERT SELL"
        desc = "Harga mencapai tinggi! Potensi jual."
    elif args.mode == "buy" and current_price <= (alert_price + 0.01):
        condition_met = True
        emoji = "🟢"
        title = "ALERT BUY"
        desc = "Harga turun ke rendah! Potensi beli."
    
    if not alert_sent and condition_met:
        alert_message = f"{emoji} <b>{title} SAHAM PSAB.JK</b>\nHarga: {current_price:.2f} IDR ({desc})\nWaktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S WIB')}\n\nCek app trading segera!"
        send_telegram_alert(alert_message)
        alert_sent = True

# Loop monitoring
try:
    print(f"Memulai monitoring {symbol} ({args.mode}): Alert jika {'>=' if args.mode == 'sell' else '<='} {alert_price} IDR.")
    print(f"Update setiap {update_interval//60} menit. Hentikan dengan Ctrl+C.")
    while True:
        fetch_stock_data(symbol)
        time.sleep(update_interval)
except KeyboardInterrupt:
    print("\nMonitoring dihentikan.")