import requests
import os
import yfinance as yf
from datetime import datetime

def get_txf_data():
    """ 
    優化後的台指期抓取邏輯 (含夜盤)
    避開 HTML 解析困難，直接讀取 Yahoo 股市 JSON API
    """
    url = "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getStockList;symbols=WTX%26"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://tw.stock.yahoo.com/quote/WTX&'
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data and len(data) > 0:
                price = data[0].get('price')
                change = data[0].get('changeValue', 0)
                return f"台指期：{float(price):.0f} ({float(change):+.0f})"
    except Exception:
        # 修正之前截圖中的語法錯誤：補齊 except 區塊
        pass 
    return "台指期：暫時無法獲取數據"

def main():
    # 1. 抓取美股 (維持 yfinance 功能)
    try:
        dji_data = yf.Ticker('^DJI').history(period='2d')
        nas_data = yf.Ticker('^IXIC').history(period='2d')
        dji = f"道瓊：{dji_data['Close'].diff().iloc[-1]:+.2f}"
        nas = f"NASDAQ：{nas_data['Close'].diff().iloc[-1]:+.2f}"
    except Exception:
        dji, nas = "道瓊：讀取失敗", "NASDAQ：讀取失敗"
    
    # 2. 抓取台指期 (使用優化後的 JSON API 邏輯)
    txf = get_txf_data()

    # 3. 組合訊息
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    msg = f"📊 市場快訊 ({now})\n{dji}\n{nas}\n{txf}"
    
    # 4. 發送到 LINE 群組
    # 請確保環境變數中的 LINE_GROUP_ID 是以 'C' 開頭的群組 ID
    token = os.environ.get('oPKb3CXX6/mN3iJe/at1Zi6uNKhcS6ws9BRVHpBsNWg0+R4auyzuCz/oF2M8jPhFKAKTF5NeT0Z25ykLkpycg3xoHJowzsruCTfB32pmW5Nts5mptbBVFTyY+qMWGBbuWet/++Jjd9aAKHPrXPTSFwdB04t89/1O/w1cDnyilFU=')
    group_id = os.environ.get('Ua323e1a963c79b9b5b6ec0affa47dd2e') # 改為讀取群組 ID
    
    if not token or not group_id:
        print("❌ 錯誤：找不到 CHANNEL_ACCESS_TOKEN 或 GROUP_ID 環境變數")
        return

    headers = {
        "Content-Type": "application/json", 
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "to": group_id, # 發送對象改為群組 ID
        "messages": [{"type": "text", "text": msg}]
    }
    
    response = requests.post(
        "https://api.line.me/v2/bot/message/push", 
        headers=headers, 
        json=payload
    )
    
    if response.status_code == 200:
        print(f"✅ 訊息已成功發送到群組：{group_id}")
    else:
        print(f"❌ 發送失敗，狀態碼：{response.status_code}，錯誤訊息：{response.text}")

if __name__ == "__main__":
    main()
