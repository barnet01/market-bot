import yfinance as yf
import requests
import os
import re

def get_txf_from_yahoo_web():
    """精準對接 Yahoo 股市 WTX& 數據"""
    try:
        # 使用網頁版代碼 WTX&F (網址需編碼為 %26)
        url = "https://tw.stock.yahoo.com/quote/WTX%26F"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(url, headers=headers, timeout=10)
        
        # 搜尋網頁中的價格與漲跌數據
        # 這裡直接抓取網頁中渲染好的 price 與 change 數值
        price_match = re.search(r'\"price\":(-?\d+\.?\d*)', res.text)
        change_match = re.search(r'\"change\":(-?\d+\.?\d*)', res.text)
        
        if price_match and change_match:
            price = float(price_match.group(1))
            change = float(change_match.group(1))
            return f"台指期近一：{price:.0f} ({change:+.0f})"
        else:
            return "台指期近一：數據格式變更"
    except:
        return "台指期近一：連線超時"

def get_us_market(ticker, name):
    try:
        data = yf.Ticker(ticker).history(period="2d")
        change = data['Close'].iloc[-1] - data['Close'].iloc[-2]
        return f"{name}：{change:+.2f}"
    except:
        return f"{name}: 獲取失敗"

def main():
    # 1. 抓取數據
    dji = get_us_market("^DJI", "道瓊指數")
    nas = get_us_market("^IXIC", "NASDAQ")
    txf = get_txf_from_yahoo_web()

    # 2. 組合訊息
    msg = f"📊 市場快訊\n{dji}\n{nas}\n{txf}"
    
    # 3. LINE 發送
    token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    uid = os.environ.get('LINE_USER_ID')
    
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = {"to": uid, "messages": [{"type": "text", "text": msg}]}
    
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    main()
