import yfinance as yf
import requests
import os
import re

def get_us_market(ticker_symbol, name):
    try:
        data = yf.Ticker(ticker_symbol).history(period="2d")
        if len(data) < 2: return f"{name}: 無數據"
        change = data['Close'].iloc[-1] - data['Close'].iloc[-2]
        return f"{name}：{change:+.2f}"
    except:
        return f"{name}: 抓取失敗"

def get_txf_night():
    """直接從 Yahoo 股市爬取台指期夜盤近月數據"""
    try:
        # 台指期近月代碼在 Yahoo 股市通常是 WTX&F
        url = "https://tw.stock.yahoo.com/quote/WTX%26F"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        
        # 使用正規表達式抓取漲跌點數
        # 尋找類似 ">-123</span>" 或 ">+45</span>" 的點數格式
        match = re.search(r'\"change\":(-?\d+\.?\d*)', res.text)
        if match:
            change = float(match.group(1))
            return f"台指期夜：{change:+.0f}"
        else:
            return "台指期夜：格式變動"
    except:
        return "台指期夜：抓取錯誤"

def main():
    # 抓取美股
    dji = get_us_market("^DJI", "道瓊指數")
    nas = get_us_market("^IXIC", "NASDAQ")
    
    # 抓取台指期
    txf = get_txf_night()

    msg = f"📊 市場快訊\n{dji}\n{nas}\n{txf}"
    
    # LINE 推播
    token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    user_id = os.environ.get('LINE_USER_ID')
    
    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = {"to": user_id, "messages": [{"type": "text", "text": msg}]}
    
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    main()
