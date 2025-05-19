import os
import time
import threading
from datetime import datetime, timedelta
import pytz
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from flask import Flask

# Flaskアプリ起動（Renderで必要）
app = Flask(__name__)

# 環境変数からメール設定を取得
gmail_address = os.environ.get("GMAIL_ADDRESS")
gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
to_address = os.environ.get("TO_ADDRESS")

# ⏰ 日本時間を設定
JST = pytz.timezone('Asia/Tokyo')

def wait_until_next_5am():
    now = datetime.now(JST)
    next_5am = JST.localize(datetime(now.year, now.month, now.day, 22, 0, 0))
    if now >= next_5am:
        next_5am += timedelta(days=1)
    wait_seconds = (next_5am - now).total_seconds()
    print(f"🕐 次の5時まで {int(wait_seconds)} 秒待ちます")
    time.sleep(wait_seconds)

def fetch_and_send_event():
    try:
        url = 'https://sunabaco.com/event/'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        event_wrap = soup.find('div', class_='eventWrap')

        if event_wrap:
            events = event_wrap.find_all('a', href=True)
            event_list = []
            for event in events:
                link = event['href']
                title_tag = event.select_one('h4.eventCard__name')
                date_tag = event.select_one('span.eventCard__date')

                title = title_tag.get_text(strip=True) if title_tag else 'タイトル不明'
                date = date_tag.get_text(strip=True) if date_tag else '日付不明'

                event_info = f"タイトル: {title}\n日付: {date}\nリンク: {link}\n"
                event_list.append(event_info)
        else:
            event_list = []

        # メール本文
        if not event_list:
            body = "現在、イベント情報は見つからなかったよ〜😢"
        else:
            body = "\n---\n".join(event_list)

        # メール作成
        msg = MIMEText(body)
        msg['Subject'] = 'SUNABACO イベント情報（ギャル通知）'
        msg['From'] = gmail_address
        msg['To'] = to_address

        # メール送信
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_address, gmail_app_password)
            smtp.send_message(msg)

        print("✨💌 ギャル通知送ったよ〜！💖")

    except Exception as e:
        print("⚠️ エラーが発生したよ！内容：", e)

# メール送信を毎日5時に行うスレッド
def schedule_loop():
    while True:
        wait_until_next_5am()
        print("✅ 朝5時だよ！スクレイピング開始")
        fetch_and_send_event()

# Flaskのルート（アクセス確認用）
@app.route('/')
def index():
    return '🌞 Render上で動いてます！'

# Flask起動時にバックグラウンドでスケジューラーを起動
if __name__ == '__main__':
    thread = threading.Thread(target=schedule_loop)
    thread.daemon = True
    thread.start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
