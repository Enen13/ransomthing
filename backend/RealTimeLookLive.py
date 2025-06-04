import json
import os
import re
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient

# === Chrome + TOR 설정 ===
chromedriver_path = "C:\\DEEP_DIVE\\TorCrawling\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

proxy_address = "127.0.0.1:9150"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(f"--proxy-server=socks5://{proxy_address}")

service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# === MongoDB 연결 ===
mongo_uri = "mongodb+srv://lch5159:dl2ckd3gus3@ransomcrawl.mmnwun3.mongodb.net/?retryWrites=true&w=majority&appName=RansomCrawl"
mongo_client = MongoClient(mongo_uri)
mongo_db = mongo_client['ransomware_db']
mongo_collection = mongo_db['detect']

# === JSON 저장 경로 설정 ===
base_dir = os.path.dirname(os.path.abspath(__file__))
detect_dir = os.path.join(base_dir, 'detect')
if not os.path.exists(detect_dir):
    os.makedirs(detect_dir)

# 중복 방지용 title 캐시
last_processed_titles = set()

# JSON 번호 증가
def get_next_detect_dir_number():
    files = [f for f in os.listdir(detect_dir) if re.match(r"detect_(\d+)\.json", f)]
    max_num = 0
    for f in files:
        m = re.match(r"detect_(\d+)\.json", f)
        if m:
            num = int(m.group(1))
            if num > max_num:
                max_num = num
    return max_num + 1

# MongoDB 업로드 함수
def upload_to_mongodb(data):
    try:
        # 기존 데이터 중복 체크
        existing = mongo_collection.find_one({
            'title': data['title'],
            'group': data['group'],
            'date': data['date']
        })
        
        if not existing:
            data['processed'] = False  # 알림 처리 여부 플래그
            result = mongo_collection.insert_one(data)
            print(f"✅ MongoDB 업로드 완료 (ID: {result.inserted_id})")
            return result.inserted_id
        else:
            print("⏩ 이미 존재하는 데이터 (중복 건너뜀)")
            return existing['_id']
    except Exception as e:
        print(f"❌ MongoDB 업로드 실패: {e}")
        return None

# 그룹 정보 크롤링
def crawl_detect_dir(group):
    if group == "j group":
        group_name = "J"
    else:
        group_name = group.replace(" ", "").lower()

    url = f"https://www.ransomware.live/group/{group_name}"
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    summary = soup.find("div", class_="d-flex justify-content-around my-4 flex-wrap gap-3")
    victims_count = last_victim = first_victim = avg_delay = infostealer = ""

    if summary:
        cards = summary.find_all("div", class_="bg-light")
        for card in cards:
            h6 = card.find("h6")
            value = (card.find("h3") or card.find("h4")).get_text(strip=True) if card.find("h3") or card.find("h4") else ""
            if h6:
                title = h6.get_text(strip=True)
                if "Victims" in title:
                    try: victims_count = int(value)
                    except: victims_count = value
                elif "First Discovered" in title: first_victim = value
                elif "Last Discovered" in title: last_victim = value
                elif "Avg Delay" in title: avg_delay = value
                elif "Infostealer" in title: infostealer = value

    target_data = []
    target_section = soup.find(id="target-section")
    if target_section:
        for card in target_section.find_all("div", class_="card"):
            header = card.find("div", class_="card-header")
            if not header: continue
            title = header.get_text(strip=True)
            items = card.find_all("li", class_="list-group-item")
            data_dict = {}
            for item in items:
                spans = item.find_all("span")
                if len(spans) >= 2:
                    key = spans[0].get_text(strip=True)
                    try: value = int(spans[1].get_text(strip=True))
                    except: value = ""
                    data_dict[key] = value
            target_data.append({title: [data_dict]})

    victims = []
    victim_list = soup.find(id="victim-list")
    if victim_list:
        for v in victim_list.find_all("div", class_="d-flex flex-column text-start flex-grow-1"):
            v_name = v.find("a", class_="text-body-emphasis text-decoration-none")
            v_name = v_name.get_text(strip=True) if v_name else ""
            discovery_date = estimated_attack_date = ""
            date_div = v.find("div", class_="text-body-secondary mt-2")
            if date_div:
                for strong in date_div.find_all("strong"):
                    label = strong.get_text(strip=True)
                    sibling = strong.next_sibling
                    if label == "Discovery Date:" and sibling:
                        discovery_date = str(sibling).strip()
                    elif label == "Estimated Attack Date:" and sibling:
                        estimated_attack_date = str(sibling).strip()
            desc_div = v.find("div", class_="p-2 rounded shadow-sm text-body-secondary bg-body-secondary")
            v_description = desc_div.get_text(strip=True) if desc_div else ""
            victims.append({
                "v_name": v_name,
                "Discovery Date": discovery_date,
                "Estimated Attack Date": estimated_attack_date,
                "v_description": v_description
            })

    return {
        "Victims count": victims_count,
        "Last discovered victim": last_victim,
        "First discovered victims": first_victim,
        "Avg Delay": avg_delay,
        "Infostealer": infostealer,
        "Target": target_data,
        "victims": victims
    }

# 최신 title 추출
def get_latest_titles(n=100):
    driver.get("http://ransomlookumjrc6erzqn467lkcu2t5h4enjzfigvsxrrktxicysi2yd.onion/recent")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.find_all("tr")
    titles = []
    for row in rows[1:n+1]:
        tds = row.find_all("td")
        if len(tds) > 1:
            titles.append(tds[1].get_text(strip=True))
    return titles

# 메인 크롤링 함수
def crawl_files():
    global last_processed_titles
    driver.get("http://ransomlookumjrc6erzqn467lkcu2t5h4enjzfigvsxrrktxicysi2yd.onion/recent")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.find_all("tr")

    if len(rows) <= 1:
        print("❌ 테이블에 데이터가 없습니다.")
        return

    post_datas = []
    for row in rows[1:101]:
        tds = row.find_all("td")
        if len(tds) > 1:
            date_str = tds[0].get_text(strip=True)
            title = tds[1].get_text(strip=True)
            group = tds[2].find("a").get_text(strip=True) if len(tds) > 2 and tds[2].find("a") else ""
            if title in last_processed_titles:
                continue

            detect_dir_data = crawl_detect_dir(group)
            post_data = {
                "date": date_str,
                "title": title,
                "group": group,
                **detect_dir_data,
                "crawled_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            post_datas.append(post_data)

    if post_datas:
        for post in post_datas:
            num = get_next_detect_dir_number()
            filename = os.path.join(detect_dir, f"detect_{num}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(post, f, ensure_ascii=False, indent=4)
            print(f"📁 저장 완료: {filename}")
            upload_to_mongodb(post)
    else:
        print("새로운 게시글이 없습니다.")

    last_processed_titles.update(get_latest_titles(100))

# === 메인 루프 ===
if __name__ == "__main__":
    try:
        last_processed_titles = set(get_latest_titles(100))
        print("🔄 시작합니다.")
        while True:
            crawl_files()
            wait = random.randint(30, 90)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n⏳ {current_time} 기준, {wait}초 후 다음 크롤링...")

            time.sleep(wait)
    except KeyboardInterrupt:
        print("\n🛑 사용자 종료")
    finally:
        driver.quit()
        mongo_client.close()
