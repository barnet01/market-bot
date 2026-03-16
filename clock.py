import requests
import os
import re
import yfinance as yf
import json  # 必須加入這行

def get_txf_backup():
    """備援來源：從玩股網抓取台指期夜盤近月數據"""
    try:
        url = "https://www.wantgoo.com/investor/futures/wtxf"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        price = re.search(r'\"lastPrice\":(\d+\.?\d*)', res.text).group(1)
        change = re.search(r'\"changeValue\":(-?\d+\.?\d*)', res.text).group(1)
        return f"台指期(備援)：{float(price):.0f} ({float(change):+.0f})"
    except:
        return "台指期：所有來源皆失敗"

def get_txf_primary():
    """主要來源：Yahoo 股市網頁版 (WTX&F)"""
    try:
        url = "https://tw.stock.yahoo.com/quote/WTX%26F"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        price = re.search(r'\"price\":(-?\d+\.?\d*)', res.text).group(1)
        change = re.search(r'\"change\":(-?\d+\.?\d*)', res.text).group(1)
        return f"台指期：{float(price):.0f} ({float(change):+.0f})"
    except:
        return None

def main():
    # 1. 抓取美股
    try:
        dji = f"道瓊：{yf.Ticker('^DJI').history(period='2d')['Close'].diff().iloc[-1]:+.2f}"
        nas = f"NASDAQ：{yf.Ticker('^IXIC').history(period='2d')['Close'].diff().iloc[-1]:+.2f}"
    except:
        dji, nas = "道瓊：抓取失敗", "NASDAQ：抓取失敗"
    
    # 2. 抓取台指期
    txf = get_txf_primary()
    if txf is None:
        txf = get_txf_backup()

    # 3. 組合並廣播發送
    msg = f"📊 市場快訊\n{dji}\n{nas}\n{txf}"
    token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    
    if not token:
        print("❌ 錯誤：找不到 LINE_CHANNEL_ACCESS_TOKEN 環境變數")
        return

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    payload = {"messages": [{"type": "text", "text": msg}]}

    # 關鍵修正：改用 json=payload 以避免編碼問題與格式錯誤
    response = requests.post(
        "https://api.line.me/v2/bot/message/broadcast", 
        headers=headers, 
        json=payload
    )

    if response.status_code == 200:
        print("✅ 群發訊息成功！")
    else:
        print(f"❌ 發送失敗，錯誤碼：{response.status_code}")
        print(f"詳細原因：{response.text}")

if __name__ == "__main__":
    main()
