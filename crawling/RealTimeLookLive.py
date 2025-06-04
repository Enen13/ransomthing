import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re
import random

# 크롬드라이버 및 TOR 프록시 설정
chromedriver_path = "C:\\DEEP_DIVE\\TorCrawling\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
proxy_address = "127.0.0.1:9150"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(f"--proxy-server=socks5://{proxy_address}")

# Selenium WebDriver 초기화
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 최근에 저장한 title 목록 (중복 저장 방지용)
last_processed_titles = set()

# 각 그룹의 상세 정보를 크롤링하는 함수
def crawl_group_info(group):
    if group == "j group": # 특수한 그룹명 처리
        group_name = "J"
    else:
        group_name = group.replace(" ", "").lower()
    base_url = f"https://www.ransomware.live/group/{group_name}"
    driver.get(base_url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    victims_count = None
    last_victim = None
    first_victim = None
    avg_delay = None
    infostealer = None

    # 카드형 div에서 정보 추출
    summary_section = soup.find("div", class_="d-flex justify-content-around my-4 flex-wrap gap-3")
    if summary_section:
        cards = summary_section.find_all("div", class_="bg-light")
        for card in cards:
            h6 = card.find("h6")
            value_tag = card.find("h3") or card.find("h4")
            value = value_tag.get_text(strip=True) if value_tag else ""
            if h6:
                title = h6.get_text(strip=True)
                if "Victims" in title:
                    try:
                        victims_count = int(value)
                    except:
                        victims_count = value
                elif "First Discovered" in title:
                    first_victim = value
                elif "Last Discovered" in title:
                    last_victim = value
                elif "Avg Delay" in title:
                    avg_delay = value
                elif "Infostealer" in title:
                    infostealer = value
                
    # Top 5 Activity Sectors, Top 5 Countries 추출
    target_section = soup.find(id="target-section")
    target_data = []
    if target_section:
        cards = target_section.find_all("div", class_="card")
        for card in cards:
            card_header = card.find("div", class_="card-header")
            if not card_header:
                continue
            title = card_header.get_text(strip=True)
            items = card.find_all("li", class_="list-group-item")
            data_dict = {}
            for item in items:
                spans = item.find_all("span")
                if len(spans) >= 2:
                    key = spans[0].get_text(strip=True)
                    try:
                        value = int(spans[1].get_text(strip=True))
                    except:
                        value = ""
                    data_dict[key] = value
            target_data.append({title: [data_dict]})
            
    # 피해자 리스트 추출
    victims = []
    victim_list = soup.find(id="victim-list")
    if victim_list:
        victim_cards = victim_list.find_all("div", class_="d-flex flex-column text-start flex-grow-1")
        for v in victim_cards:
            v_name_tag = v.find("a", class_="text-body-emphasis text-decoration-none")
            v_name = v_name_tag.get_text(strip=True) if v_name_tag else ""
            date_div = v.find("div", class_="text-body-secondary mt-2")
            discovery_date = ""
            estimated_attack_date = ""
            if date_div:
                strong_tags = date_div.find_all("strong")
                for strong in strong_tags:
                    label = strong.get_text(strip=True)
                    if label == "Discovery Date:":
                        next_sibling = strong.next_sibling
                        if next_sibling:
                            discovery_date = str(next_sibling).strip()
                    elif label == "Estimated Attack Date:":
                        next_sibling = strong.next_sibling
                        if next_sibling:
                            estimated_attack_date = str(next_sibling).strip()
            desc_div = v.find("div", class_="p-2 rounded shadow-sm text-body-secondary bg-body-secondary")
            v_description = desc_div.get_text(strip=True) if desc_div else ""
            victims.append({
                "v_name": v_name,
                "Discovery Date": discovery_date,
                "Estimated Attack Date": estimated_attack_date,
                "v_description": v_description
            })
            
    group_info_data = {
        "Victims count": victims_count if victims_count is not None else "",
        "Last discovered victim": last_victim if last_victim is not None else "",
        "First discovered victims": first_victim if first_victim is not None else "",
        "Avg Delay": avg_delay if avg_delay is not None else "",
        "Infostealer": infostealer if infostealer is not None else "",   
        "Target": target_data,
        "victims": victims
    }
    return group_info_data

# 최근 n개 게시글의 title을 리스트로 반환
def get_latest_titles(n=100):
    driver.get("http://ransomlookumjrc6erzqn467lkcu2t5h4enjzfigvsxrrktxicysi2yd.onion/recent")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.find_all("tr")
    titles = []
    for row in rows[1:n+1]:
        tds = row.find_all("td")
        if len(tds) > 1:
            title = tds[1].get_text(strip=True)
            titles.append(title)
    return titles

# detect_*.json 파일 중 가장 큰 번호를 찾아 다음 번호 반환
def get_next_detect_number():
    files = [f for f in os.listdir() if re.match(r"detect_(\d+)\.json", f)]
    max_num = 0
    for f in files:
        m = re.match(r"detect_(\d+)\.json", f)
        if m:
            num = int(m.group(1))
            if num > max_num:
                max_num = num
    return max_num + 1

# 실제로 게시글을 크롤링하고 저장하는 메인 함수
def crawl_files():
    global last_processed_titles
    driver.get("http://ransomlookumjrc6erzqn467lkcu2t5h4enjzfigvsxrrktxicysi2yd.onion/recent")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.find_all("tr")
    # 1분마다 첫 번째 행의 title 출력
    if len(rows) > 1:
        tds = rows[1].find_all("td")
        first_title = tds[1].get_text(strip=True) if len(tds) > 1 else ""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 현재 첫 번째 행의 title: {first_title}")
    else:
        print("테이블에 데이터가 없습니다.")

    post_datas = []
    # 최근 100개 행 중 새로운 게시글만 post_datas에 저장
    for row in rows[1:101]:
        tds = row.find_all("td")
        if len(tds) > 1:
            date_str = tds[0].get_text(strip=True)
            title = tds[1].get_text(strip=True)
            group = tds[2].find("a").get_text(strip=True) if len(tds) > 2 and tds[2].find("a") else ""
            if title not in last_processed_titles:
                group_details = []
                if group:
                    group_url = f"http://ransomlookumjrc6erzqn467lkcu2t5h4enjzfigvsxrrktxicysi2yd.onion/group/{group}"
                    driver.get(group_url)
                    time.sleep(3)
                    group_soup = BeautifulSoup(driver.page_source, "html.parser")
                    posts_h4 = group_soup.find("h4", string="Posts")
                    tbody = None
                    if posts_h4:
                        next_elem = posts_h4
                        while next_elem:
                            next_elem = next_elem.find_next()
                            if next_elem and next_elem.name == "tbody":
                                tbody = next_elem
                                break
                    if tbody:
                        g_rows = tbody.find_all("tr")
                        for g_row in g_rows:
                            g_tds = g_row.find_all("td")
                            g_date = g_tds[0].get_text(strip=True) if len(g_tds) > 0 else ""
                            g_title = g_tds[1].get_text(strip=True) if len(g_tds) > 1 else ""
                            g_description = g_tds[2].get_text(strip=True) if len(g_tds) > 2 else ""
                            group_details.append({
                                "g_date": g_date,
                                "g_title": g_title,
                                "g_description": g_description
                            })
                group_info_data = crawl_group_info(group)
                post_data = {
                    "date": date_str,
                    "title": title,
                    "group": group,
                    "group_details": group_details,
                    **group_info_data
                }
                post_datas.append(post_data)
    # 새로 추가된 글이 있다면 각각 저장 (아래 행부터 순서대로)
    if post_datas:
        next_num = get_next_detect_number()
        for post_data in reversed(post_datas):  # 아래 행부터 저장
            filename = f"detect_{next_num}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(post_data, f, ensure_ascii=False, indent=4)
            print(f"{filename} 파일 저장 완료.")
            next_num += 1
    else:
        print("새로운 게시글이 탐지되지 않았습니다.")
    # 최신 title 목록 갱신 (최신 100개)
    latest_titles = get_latest_titles(100)
    last_processed_titles = set(latest_titles)

if __name__ == "__main__":
    try:
        # 최초 실행 시 최신글 title 목록 저장
        last_processed_titles = set(get_latest_titles(100))
        print(f"최초 실행시 최신글 title 목록: {last_processed_titles}")
        while True:
            try:
                crawl_files()
            except Exception as e:
                print(f"크롤링 중 오류 발생: {e}")
            wait_time = random.randint(30, 120)  # 30초~120초 사이 랜덤
            print(f"{wait_time}초 후 다음 크롤링을 진행합니다.")
            time.sleep(wait_time)
    finally:
        driver.quit()