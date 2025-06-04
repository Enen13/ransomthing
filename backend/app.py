import os
import sys
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from pymongo import MongoClient
from datetime import datetime
import threading
import time
import json
from search_bot.chatbot_api import ChatbotService
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
chatbot = ChatbotService()

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ALERT_LOG_FILE = os.path.join(PROJECT_DIR, "latest_alerts.json")

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "search_bot"))

# MongoDB 연결 설정
uri = ""
client = MongoClient(uri)
db = client['ransomware_db']
collection = db['group_info']

def load_messages():
    """latest_alerts.json에서 메시지만 추출"""
    try:
        if os.path.exists(ALERT_LOG_FILE):
            with open(ALERT_LOG_FILE, 'r', encoding='utf-8') as f:
                alerts_data = json.load(f)
                return [alert['message'] for alert in alerts_data if 'message' in alert]
    except Exception as e:
        print(f"⚠️ 알림 로드 오류: {e}")
    return ["현재 새로운 알림이 없습니다."]

@app.route('/')
def index():
    messages = load_messages()
    return render_template('index.html', alerts=messages)

@app.route('/get_alerts')
def get_alerts():
    messages = load_messages()
    return jsonify({"alerts": messages})

@app.route('/worldmap')#세계지도 히트맵
def worldmap():
    return render_template('worldmap.html')

@app.route('/external')#추가 링크클릭
def external_link():
    return redirect("https://www.example.com")

@app.route('/api/chatbot', methods=['POST'])
def chatbot_handler():
    command = request.json.get('command')
    query = request.json.get('query', '')

    try:
        if command == "search":
            result = chatbot.handle_search(query)
        elif command == "attack_rank":
            result = {"data": chatbot.handle_attack_rank()}
        elif command == "today_attacks":
            result = {"data": chatbot.handle_today_attacks()}
        else:
            result = {"error": "지원하지 않는 명령어입니다."}
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"서버 오류: {str(e)}"}), 500

@app.route('/debug_date')
def debug_date():
    today_server = datetime.now().strftime("%Y-%m-%d")
    today_kst = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d")
    json_dates = list(set(rec[0] for rec in chatbot.latest_attack if len(rec) >= 1))

    return jsonify({
        "server_date_utc": today_server,
        "server_date_kst": today_kst,
        "json_dates": json_dates,
        "is_today_in_json": "2025-06-03" in json_dates  # 테스트용 하드코딩 날짜
    })
    
if __name__ == '__main__':
    app.run(debug=True)