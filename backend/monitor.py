import os
import time
import json
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

# MongoDB 설정
MONGO_URI = "mongodb+srv://lch5159:dl2ckd3gus3@ransomcrawl.mmnwun3.mongodb.net/?retryWrites=true&w=majority&appName=RansomCrawl"
DB_NAME = 'ransomware_db'
COLLECTION_NAME = 'detect'

# 경로 설정
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ALERT_LOG_FILE = os.path.join(PROJECT_DIR, "latest_alerts.json")
MAX_ALERTS = 10
CHECK_INTERVAL = 10  # 초

class AlertMonitor:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]
        self.last_processed_id = self._get_last_processed_id()

    def _get_last_processed_id(self):
        """마지막으로 처리된 문서의 ID 조회"""
        try:
            if os.path.exists(ALERT_LOG_FILE):
                with open(ALERT_LOG_FILE, 'r', encoding='utf-8') as f:
                    # 파일 내용이 비어있을 경우 처리
                    content = f.read().strip()
                    if not content:
                        return None
                        
                    data = json.loads(content)
                    # 데이터가 리스트인지 확인
                    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                        return ObjectId(data[0].get('_id'))
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
            print(f"⚠️ 경고: 알림 파일 읽기 오류 - {e}")
            # 오류 발생 시 파일 재생성
            with open(ALERT_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
        return None

    def _save_alerts(self, alerts):
        """알림 목록 저장 (유니코드 이스케이프 방지)"""
        try:
            with open(ALERT_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(alerts, f, indent=2, ensure_ascii=False, default=str)
            print(f"✅ 알림 파일 저장 완료: {ALERT_LOG_FILE}")
        except Exception as e:
            print(f"❌ 파일 저장 실패: {e}")

    def check_new_alerts(self):
        """새로운 알림 확인"""
        query = {}
        if self.last_processed_id:
            query = {'_id': {'$gt': self.last_processed_id}}

        try:
            new_docs = list(self.collection.find(query).sort('_id', -1).limit(MAX_ALERTS))
            
            if new_docs:
                alerts = []
                for doc in new_docs:
                    alert = {
                        '_id': str(doc['_id']),
                        'message': f"📢 [새로운 랜섬웨어 감지 - {doc.get('group', 'Unknown')}] "
                                  f"🗓 날짜: {doc.get('date', '')} "
                                  f"📌 제목: {doc.get('title', '')}",
                        'timestamp': datetime.now().isoformat()
                    }
                    alerts.append(alert)
                
                self._save_alerts(alerts)
                self.last_processed_id = new_docs[0]['_id']
                print(f"✅ 새로운 알림 {len(new_docs)}개 처리 완료")
                return True
        except Exception as e:
            print(f"❌ MongoDB 쿼리 오류: {e}")
        return False

    def run(self):
        print("🚀 알림 모니터링 서비스 시작")
        try:
            while True:
                self.check_new_alerts()
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\n🛑 사용자 종료")
        finally:
            self.client.close()

if __name__ == "__main__":
    # 최초 실행 시 알림 파일 초기화
    if not os.path.exists(ALERT_LOG_FILE):
        with open(ALERT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    
    monitor = AlertMonitor()
    monitor.run()