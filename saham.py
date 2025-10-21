# TO RUN in virtual env:
# py -m venv venv
# venv\Scripts\activate  # Aktifkan env (di Windows)
# pip install yfinance pandas
# py yfinance.py

import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# Simbol saham IDX: PSAB.JK (untuk PT Panca Satria Abadi)
symbol = "PSAB.JK"

# Fungsi untuk fetch data intraday real-time
def fetch_stock_data(symbol, interval='1m', period='1d'):
    ticker = yf.Ticker(symbol)
    
    # Ambil data historis intraday (terdekat real-time)
    data = ticker.history(period=period, interval=interval)
    
    # Ambil bar terakhir (paling baru)
    latest = data.iloc[-1]
    
    # Info tambahan dari fast_info (lebih cepat untuk real-time)
    fast_info = ticker.fast_info
    
    print(f"\n=== Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"Saham: {symbol}")
    print(f"Harga Terakhir: {latest['Close']:.2f} IDR")
    print(f"Open: {latest['Open']:.2f} | High: {latest['High']:.2f} | Low: {latest['Low']:.2f}")
    print(f"Volume: {latest['Volume']:,}")
    print(f"Change: {latest['Close'] - data.iloc[-2]['Close']:.2f} ({((latest['Close'] / data.iloc[-2]['Close'] - 1) * 100):.2f}%)")
    print(f"Previous Close: {fast_info.get('previousClose', 'N/A')}")
    print("=====================================")

# Loop untuk update real-time (setiap 1 menit, hentikan dengan Ctrl+C)
try:
    while True:
        fetch_stock_data(symbol)
        time.sleep(60)  # Tunggu 1 menit sebelum update berikutnya
except KeyboardInterrupt:
    print("\nStopped by user.")