import yfinance as yf
import requests
import os

def get_data(ticker_symbol, name):
    try:
        data = yf.Ticker(ticker_symbol).history(period="2d")
        if len(data) < 2:
            return f"{name}: 獲取失敗"
        change = data['Close'].iloc[-1] - data['Close'].iloc[-2]
        return f"{name}：{change:+.2f}"
    except Exception as e:
        return f"{name}: 錯誤"

def main():
    # 抓取各項指標
    nasdaq_str = get_data("^IXIC", "NASDAQ")
    dji_str = get_data("^DJI", "道瓊指數")
    
    # 台指期代碼有時會變動，若 MTX=F 不行，可換成台指期近月代碼
    txf_str = get_data("MTX=F", "台指期夜") 

    msg = f"📊 市場快訊\n{dji_str}\n{nasdaq_str}\n{txf_str}"
    
    # LINE 推播
    token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    user_id = os.environ.get('LINE_USER_ID')
    
    if not token or not user_id:
        print("錯誤：找不到 Secrets 設定！")
        return

    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = {"to": user_id, "messages": [{"type": "text", "text": msg}]}
    
    res = requests.post(url, headers=headers, json=payload)
    print(f"發送狀態: {res.status_code}")

if __name__ == "__main__":
    main()
