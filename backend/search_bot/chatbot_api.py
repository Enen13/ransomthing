import os
import json
from datetime import datetime

# 파일 경로 설정 (상대 경로)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GROUP_INFO_PATH = os.path.join(BASE_DIR, "group_infomation.json")
ATTACK_RANK_PATH = os.path.join(BASE_DIR, "attack_ranking.json")
LATEST_ATTACK_PATH = os.path.join(BASE_DIR, "latest_attack.json")

class ChatbotService:
    def __init__(self):
        # 파일 경로를 search_bot 폴더 내로 지정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.GROUP_INFO_PATH = os.path.join(current_dir, "group_infomation.json")
        self.ATTACK_RANK_PATH = os.path.join(current_dir, "attack_ranking.json")
        self.LATEST_ATTACK_PATH = os.path.join(current_dir, "latest_attack.json")
        self.load_data()

    def load_data(self):
        """필요한 데이터 파일 로드"""
        try:
            with open(GROUP_INFO_PATH, encoding="utf-8") as f:
                self.group_info = json.load(f)
            with open(ATTACK_RANK_PATH, encoding="utf-8") as f:
                self.attack_rank = json.load(f)
            with open(LATEST_ATTACK_PATH, encoding="utf-8") as f:
                self.latest_attack = json.load(f)
        except FileNotFoundError as e:
            raise RuntimeError(f"데이터 파일 로드 실패: {e}")

    def normalize(self, s: str) -> str:
        return "" if not s else s.lower().replace(" ", "")

    def clean(self, v):
        if v is None or (isinstance(v, str) and v.strip().lower() in {"", "n/a", "null", "none"}):
            return "없음"
        return str(v)

    def handle_search(self, query: str) -> dict:
        """그룹 검색 처리"""
        query_normalized = self.normalize(query)
        match = next((g for g in self.group_info 
                     if self.normalize(g.get("그룹 이름")) == query_normalized), None)
        
        if not match:
            return {"error": f"'{query}' 그룹 정보가 없습니다."}
        
        return {
            "title": match.get("그룹 이름", query),
            "fields": [
                {"name": "공격 횟수", "value": self.clean(match.get("공격 횟수"))},
                {"name": "최근 공격일", "value": self.clean(match.get("그룹의 최근 공격일"))},
                {"name": "처음 공격일", "value": self.clean(match.get("그룹의 첫 공격일"))}
            ],
            "url": match.get("URL", "")
        }

    def handle_attack_rank(self) -> list:
        """공격 횟수 순위 처리"""
        return [
            {"rank": i+1, "name": g.get("그룹 이름", ""), "count": g.get("공격 횟수", "")}
            for i, g in enumerate(self.attack_rank)
        ]

    def handle_today_attacks(self) -> list:
        """오늘의 공격 현황 처리"""
        today = datetime.now().strftime("%Y-%m-%d")
        return [
            {"group": rec[2], "domain": rec[1]}
            for rec in self.latest_attack 
            if len(rec) == 3 and rec[0] == today
        ]