import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os

# ChromeDriver 경로
chromedriver_path = "C:\\DEEP_DIVE\\TorCrawling\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

# Selenium WebDriver 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

# WebDriver 초기화
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

base_url = "https://www.ransomware.live"

def crawl_group_info(group_url, group_id, group_names):
    driver.get(group_url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 그룹명과 설명 추출
    group_description = ""
    group_info_section = soup.find("div", class_="container-fluid px-lg-5 my-3")
    if group_info_section:
        desc_div = group_info_section.find("div", class_="mt-2 p-2 rounded shadow-sm text-body-secondary w-100 bg-body-secondary")
        if desc_div:
            group_description = desc_div.get_text(strip=True)

    # 피해자 수, 마지막 피해자 발견일, 첫 피해자 발견일, Avg Delay, Infostealer 추출
    victims_count = None
    last_victim = None
    first_victim = None
    avg_delay = None
    infostealer = None

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
        "group_name": group_names,
        "group_description": group_description,
        "Victims count": victims_count if victims_count is not None else "",
        "First discovered victims": first_victim if first_victim is not None else "",
        "Last discovered victim": last_victim if last_victim is not None else "",
        "Avg Delay": avg_delay if avg_delay is not None else "",
        "Infostealer": infostealer if infostealer is not None else "",
        "Target": target_data,
        "victims": victims
    }

    # group_info 폴더가 없으면 생성
    save_dir = "group_info"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 파일명에 여러 이름을 _로 연결해서 저장
    file_group_name = "_".join(group_names)
    save_path = os.path.join(save_dir, f"group_info_{file_group_name}.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(group_info_data, f, ensure_ascii=False, indent=4)
    print(f"{save_path} 파일 저장 완료.")

def crawl_all_groups():
    driver.get(f"{base_url}/groups")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    group_list = soup.find("ul", id="group-list")
    if not group_list:
        print("그룹 리스트를 찾을 수 없습니다.")
        return
     
    # 링크별로 여러 이름을 모두 수집
    group_dict = {}
    for li in group_list.find_all("li", class_="list-group-item"):
        fw_bold_div = li.find("div", class_="fw-bold")
        if fw_bold_div:
            for a in fw_bold_div.find_all("a", class_="text-dark text-decoration-none"):
                href = a.get("href")
                name_span = a.find("span", class_="badge bg-success fs-5")
                if href and name_span:
                    name = name_span.get_text(strip=True)
                    if href not in group_dict:
                        group_dict[href] = []
                    if name not in group_dict[href]:
                        group_dict[href].append(name)

    for href, names in group_dict.items():
        if href.startswith("/group/"):
            group_id = href.split("/group/")[1]
            group_url = base_url + href
            print(f"크롤링 시작: {group_url} ({', '.join(names)})")
            crawl_group_info(group_url, group_id, names)
            time.sleep(2)

if __name__ == "__main__":
    try:
        crawl_all_groups()
    finally:
        driver.quit()