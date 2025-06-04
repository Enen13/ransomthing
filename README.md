# Ransomthing 설치 및 실행 가이드

## 1. 프론트엔드(React) 환경 설정

### 1) 필수 프로그램
- Node.js (최소 16.x 이상 권장)
- npm (Node.js 설치 시 자동 포함)

### 2) 설치 방법
```bash
cd frontend
npm install
```

---

## 2. 백엔드(Python) 환경 설정

### 1) 필수 프로그램
- Python 3.8 이상 권장
- pip (Python 설치 시 자동 포함)
- MongoDB 서버 (로컬 또는 원격)

### 2) 가상환경(선택)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3) 필수 라이브러리 설치
```bash
pip install flask pymongo bson selenium beautifulsoup4 pandas numpy matplotlib seaborn python-dotenv plotly geopandas pycountry
```

---

## 3. 기타

- **셀레니움 사용 시 크롬 드라이버 필요**
  - [크롬 드라이버 다운로드](https://chromedriver.chromium.org/downloads)
  - 드라이버 경로를 환경변수에 추가하거나, 코드에서 직접 경로 지정 필요

- **MongoDB**
  - 로컬 또는 원격 MongoDB 서버가 필요합니다.

---

## 4. 실행 방법

### 프론트엔드
```bash
cd frontend
npm start
```

### 백엔드
```bash
cd backend
python app.py
```
반드시 두개의 터미널 창에서 각자 실행시켜야 합니다.
---

## 5. 참고

- 추가적으로 에러가 발생할 경우, 에러 메시지에 따라 필요한 패키지를 추가로 설치해 주세요.
- `requirements.txt` 파일이 없는 경우 위 명령어로 직접 설치해야 합니다.
