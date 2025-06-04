import json
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# 현재 작업 디렉터리 기준 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
chromedriver_path = "C:\\DEEP_DIVE\\TorCrawling\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

# Selenium WebDriver 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

# WebDriver 초기화
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.implicitly_wait(5)

while True:
    # 그룹 이름 파일 로드 (상대 경로)
    group_name_path = os.path.join(BASE_DIR, "group_name.json")
    with open(group_name_path, "r", encoding="utf-8") as f:
        group_list = json.load(f)

    def slugify(name: str) -> str:
        name = name.lower().strip()
        name = re.sub(r"\s+", "", name)
        name = re.sub(r"[^\w\-]", "-", name)
        return name

    results = []
    for g in group_list:
        raw_name = g.get("group name")
        if not raw_name:
            print("⚠️  'group name' 키가 비어 있습니다:", g)
            continue

        slug = slugify(raw_name)
        url = f"https://www.ransomware.live/group/{slug}"
        print(f"➜ [{raw_name}] 페이지 접속: {url}")

        try:
            driver.get(url)
            time.sleep(1)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # ─────────────────────────────────────────────
            # ① 그룹 이름
            group_name = None
            h5 = soup.find("h5")
            if h5:
                badge = h5.find("span", class_="badge bg-success")
                if badge:
                    group_name = badge.get_text(strip=True)

            # ── ② Victims count, Last/First discovered ──
            victims_count = last_discovered = first_discovered = "N/A"

            # 1) Victims count  ── /html/body/div[3]/div[3]/div[1]/h3
            vc_elem = soup.select_one("body > div:nth-of-type(3) > div:nth-of-type(3) > div:nth-of-type(1) > h3")
            if not vc_elem:                              # 다른 그룹은 class 로 나올 수도 있음
                vc_elem = soup.select_one("h3.mb-0")     # 예전 구조 백업
            victims_count = vc_elem.get_text(strip=True) if vc_elem else "N/A"

            # 2) First / Last discovered  ── 바로 옆 div 의 <h4>
            fd_elem = soup.select_one("body > div:nth-of-type(3) > div:nth-of-type(3) > div:nth-of-type(2) > h4")
            ld_elem = soup.select_one("body > div:nth-of-type(3) > div:nth-of-type(3) > div:nth-of-type(3) > h4")

            # 예전 구조 대비 백업 선택자
            if not fd_elem:
                fd_elem = soup.find("small", string=re.compile("first discovered", re.I))
                fd_elem = fd_elem.find_next("h4") if fd_elem else None
            if not ld_elem:
                ld_elem = soup.find("small", string=re.compile("last discovered", re.I))
                ld_elem = ld_elem.find_next("h4") if ld_elem else None

            first_discovered = fd_elem.get_text(strip=True) if fd_elem else "N/A"
            last_discovered  = ld_elem.get_text(strip=True) if ld_elem else "N/A"

            # ③ 추출 결과 하나로 묶기
            results.append({
                "그룹 이름": group_name or raw_name,   # 혹시 badge가 없으면 원본 이름
                "공격 횟수": victims_count,
                "그룹의 최근 공격일": last_discovered,
                "그룹의 첫 공격일": first_discovered,
                "URL": url                            # 추적 편의를 위해 기록
            })

        except Exception as e:
            print(f"‼️  {raw_name} 처리 중 오류:", e)
            continue

    ##############################################################################
    # 5. 모든 그룹 결과 저장
    ##############################################################################
    # 그룹 정보 저장 (상대 경로)
    group_info_path = os.path.join(BASE_DIR, "group_infomation.json")
    with open(group_info_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    # 공격 횟수 순위 생성
    sorted_groups = sorted(results, key=lambda x: int(x.get("공격 횟수", 0) if x.get("공격 횟수") != "N/A" else 0), reverse=True)
    top_10_groups = sorted_groups[:10]

    # 공격 순위 저장 (상대 경로)
    attack_rank_path = os.path.join(BASE_DIR, "attack_ranking.json")
    with open(attack_rank_path, "w", encoding="utf-8") as f:
        json.dump(top_10_groups, f, ensure_ascii=False, indent=4)

    print("✅ 크롤링 완료. 1시간 후에 다시 실행합니다.")
    driver.quit()
    time.sleep(3600)