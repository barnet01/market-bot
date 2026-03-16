import requests
import os
import re
import yfinance as yf

def get_txf_backup():
    """備援來源：從玩股網抓取台指期夜盤近月數據"""
    try:
        # 玩股網台指期近月頁面
        url = "https://www.wantgoo.com/investor/futures/wtxf"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers, timeout=10)
        
        # 尋找當前點數與漲跌點數
        # 玩股網的數據通常存在 class 為 "idx-data" 或特定變數中
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
        return None # 返回 None 觸發備援機制

def main():
    # 1. 抓取美股
    dji = f"道瓊：{yf.Ticker('^DJI').history(period='2d')['Close'].diff().iloc[-1]:+.2f}"
    nas = f"NASDAQ：{yf.Ticker('^IXIC').history(period='2d')['Close'].diff().iloc[-1]:+.2f}"
    
    # 2. 抓取台指期 (具備備援機制)
    txf = get_txf_primary()
    if txf is None:
        txf = get_txf_backup()

    # 3. 組合並發送
    msg = f"📊 市場快訊\n{dji}\n{nas}\n{txf}"
    
    token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    uid = os.environ.get('LINE_USER_ID')
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = {"messages": [{"type": "text", "text": msg}]}
   

    
    requests.post("https://api.line.me/v2/bot/message/broadcast", headers=headers, json.dumps(payload))

if __name__ == "__main__":
    main()
