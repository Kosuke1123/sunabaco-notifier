from flask import Flask, jsonify
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# ------------------------
# 💄 Gmail情報（Renderの環境変数に設定しておくのがおすすめ）
gmail_address = os.environ.get('GMAIL_ADDRESS')  # 例: 'example@gmail.com'
gmail_app_password = os.environ.get('GMAIL_APP_PASSWORD')  # アプリパスワード
to_address = os.environ.get('TO_ADDRESS')  # 送信先アドレス

# ------------------------

# ⏰ 日本時間
JST = pytz.timezone('Asia/Tokyo')

def fetch_event_info():
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

        if not event_list:
            body = "現在、イベント情報は見つからなかったよ〜😢"
        else:
            body = "\n---\n".join(event_list)

        return body

    except Exception as e:
        return f"⚠️ エラーが発生したよ！内容：{e}"

def send_email(body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = 'SUNABACO イベント情報（ギャル通知）'
        msg['From'] = gmail_address
        msg['To'] = to_address

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_address, gmail_app_password)
            smtp.send_message(msg)

        return "✨💌 ギャル通知送ったよ〜！💖"

    except Exception as e:
        return f"⚠️ メール送信でエラーが発生したよ：{e}"

@app.route('/')
def home():
    return '🎀 SUNABACO イベント通知アプリ 動作中 🎀'

@app.route('/run')
def run_fetch_and_send():
    print("✅ 手動実行開始")
    body = fetch_event_info()
    result = send_email(body)
    return jsonify({'status': result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

