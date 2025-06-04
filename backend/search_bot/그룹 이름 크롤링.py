import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# 현재 작업 디렉터리 기준 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
chromedriver_path = "C:\\DEEP_DIVE\\TorCrawling\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

# TOR 프록시 설정
proxy_address = "127.0.0.1:9150"

# Selenium WebDriver 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(f"--proxy-server=socks5://{proxy_address}")

# WebDriver 초기화
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 페이지 로드
driver.get("http://ransomlookumjrc6erzqn467lkcu2t5h4enjzfigvsxrrktxicysi2yd.onion/groups")

# BeautifulSoup으로 HTML 파싱
soup = BeautifulSoup(driver.page_source, "html.parser")

# h3 태그 찾기
h3_tags = soup.find_all("h3")

# 데이터 추출 및 저장
data = []
for h3 in h3_tags:
    group_name = h3.text.strip()
    data_dict = {
        "group name": group_name
    }
    data.append(data_dict)

# JSON 파일에 저장 (상대 경로)
output_path = os.path.join(BASE_DIR, "group_name.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("✅크롤링 완료")
driver.quit()