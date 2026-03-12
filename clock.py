import yfinance as yf
import requests

def get_market_data():
    # 1. 抓取美股 (NASDAQ: ^IXIC, DJI: ^DJI)
    nasdaq = yf.Ticker("^IXIC").history(period="2d")
    dji = yf.Ticker("^DJI").history(period="2d")
    
    nas_change = nasdaq['Close'].iloc[-1] - nasdaq['Close'].iloc[-2]
    dji_change = dji['Close'].iloc[-1] - dji['Close'].iloc[-2]

    # 2. 抓取台指期夜盤 (簡單示範從 Yahoo 財經或期交所抓取)
    # 註：台指期夜盤數據通常在期交所官網，或使用 yfinance 抓取代碼 'WTX&F'
    txf = yf.Ticker("MTX=F").history(period="2d") # 以微台指期貨為例
    txf_change = txf['Close'].iloc[-1] - txf['Close'].iloc[-2]

    msg = (f"📊 今日市場摘要\n"
           f"道瓊指數：{dji_change:+.2f}\n"
           f"NASDAQ：{nas_change:+.2f}\n"
           f"台指期夜盤：{txf_change:+.0f}")
    return msg

def send_line_message(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {YOUR_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "to": "{YOUR_USER_ID}",
        "messages": [{"type": "text", "text": message}]
    }
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    content = get_market_data()
    send_line_message(content)
