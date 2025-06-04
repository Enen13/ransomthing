import json
import os
import time
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

while True:
    driver.get("http://ransomlookumjrc6erzqn467lkcu2t5h4enjzfigvsxrrktxicysi2yd.onion/recent")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    tr_tags = soup.find_all("tr")

    data = []
    for tr in tr_tags:
        row = [td.text.strip() for td in tr.find_all("td")]
        data.append(row)

    # 파일 저장 (상대 경로)
    output_path = os.path.join(BASE_DIR, "latest_attack.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("크롤링 완료")
    time.sleep(60)