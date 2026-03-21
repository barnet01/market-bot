import requests
import os
import re
import yfinance as yf
import json  # 必須加入這行
from datetime import datetime
import pytz

def get_txf_night():
    """抓取台指期盤後(夜盤)數據，從期交所 API"""
    try:
        url = "https://mis.taifex.com.tw/futures/api/getQuoteList"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'Referer': 'https://mis.taifex.com.tw/futures/'
        }
        # 獲取台指期近月合約（夜盤以 -M 結尾）
        payload = {
            'SymbolID': ['TXF'],  # 台指期
        }
        res = requests.post(url, headers=headers, json=payload, timeout=10)

        if res.status_code == 200:
            data = res.json()
            quote_list = data.get('RtData', {}).get('QuoteList', [])

            # 查找近月夜盤合約（TXFC?-M 或 TXFD?-M 等）
            # 夜盤合約以 -M 結尾
            night_contract = None
            for quote in quote_list:
                symbol_id = quote.get('SymbolID', '')
                # 近月夜盤合約格式：TXFC6-M, TXFD6-M 等
                if symbol_id.startswith('TXF') and symbol_id.endswith('-M'):
                    last_price = quote.get('CLastPrice', '')
                    ref_price = quote.get('CRefPrice', '')
                    if last_price and ref_price:
                        last_price = float(last_price)
                        ref_price = float(ref_price)
                        change = last_price - ref_price
                        return f"台指期盤後：{last_price:.0f} ({change:+.0f})"

            # 如果找不到 -M 合約，嘗試使用臺指現貨 TXF-S
            for quote in quote_list:
                symbol_id = quote.get('SymbolID', '')
                if symbol_id == 'TXF-S':
                    last_price = quote.get('CLastPrice', '')
                    diff = quote.get('CDiff', '')
                    if last_price:
                        return f"台指期盤後：{float(last_price):.0f} ({float(diff):+.0f})"

        return "台指期盤後：無法獲取數據"
    except Exception as e:
        return f"台指期盤後：抓取失敗"


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

def send_market_update():
    """發送市場快訊"""
    # 獲取台灣時間
    tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tz)
    print(f"\n{'='*50}")
    print(f"📅 執行時間：{now.strftime('%Y-%m-%d %H:%M:%S')} (台灣時間)")
    print(f"{'='*50}\n")

    # 1. 抓取美股
    try:
        dji = f"道瓊：{yf.Ticker('^DJI').history(period='2d')['Close'].diff().iloc[-1]:+.2f}"
        nas = f"NASDAQ：{yf.Ticker('^IXIC').history(period='2d')['Close'].diff().iloc[-1]:+.2f}"
    except:
        dji, nas = "道瓊：抓取失敗", "NASDAQ：抓取失敗"
    
    # 2. 抓取台指期盤後（夜盤）
    txf_night = get_txf_night()

    # 3. 組合並廣播發送
    msg = f"📊 市場快訊\n{dji}\n{nas}\n{txf_night}"
    # 優先使用環境變數，若無則使用預設值（本地測試用）
    token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    
    if not token:
        print("❌ 錯誤：找不到 LINE_CHANNEL_ACCESS_TOKEN 環境變數")
        print("請設定環境變數：LINE_CHANNEL_ACCESS_TOKEN")
        return

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    payload = {"messages": [{"type": "text", "text": msg}]}

    response = requests.post(
        "https://api.line.me/v2/bot/message/broadcast", 
        headers=headers, 
        json=payload
    )

    if response.status_code == 200:
        print("✅ 群發訊息成功！")
        print(f"\n發送內容：\n{msg}")
    else:
        print(f"❌ 發送失敗，錯誤碼：{response.status_code}")
        print(f"詳細原因：{response.text}")

def main():
    """主函數：直接執行一次市場快訊發送"""
    # 設定台灣時區
    tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tz)
    
    print("🤖 市場快訊機器人已啟動！")
    print(f"📅 執行時間：{now.strftime('%Y-%m-%d %H:%M:%S')} (台灣時間)")
    print("📝 程式將執行一次市場快訊發送\n")
    
    # 直接執行一次
    send_market_update()
    
    print("\n✅ 執行完成，程式結束。")

if __name__ == "__main__":
    main()
