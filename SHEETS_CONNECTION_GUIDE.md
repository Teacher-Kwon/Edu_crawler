# 🔗 Google Sheets 연동 문제 해결 가이드

## 🚨 스프레드시트 연동이 안 되는 경우

### 1️⃣ 빠른 진단 및 해결

#### A. 연결 테스트 실행

```bash
# Google Sheets 연결 테스트
python test_sheets_connection.py

# 또는 진단 도구 실행
python diagnose_sheets.py
```

#### B. 문제 해결된 버전 실행

```bash
# Windows
run_with_sheets_fix.bat

# 또는 직접 실행
python main_with_sheets_fix.py
```

### 2️⃣ 일반적인 문제들 및 해결방법

#### ❌ 문제 1: "credentials.json 파일이 없습니다"

**해결방법:**

1. Google Cloud Console (https://console.cloud.google.com) 접속
2. 프로젝트 선택 또는 새 프로젝트 생성
3. "API 및 서비스" > "라이브러리"에서 "Google Sheets API" 활성화
4. "API 및 서비스" > "사용자 인증 정보"에서 서비스 계정 생성
5. 서비스 계정 키 다운로드 (JSON 형식)
6. 다운로드한 파일을 `credentials.json`으로 이름 변경
7. 프로젝트 폴더에 저장

#### ❌ 문제 2: "스프레드시트에 접근할 수 없습니다"

**해결방법:**

1. Google Sheets에서 스프레드시트 열기
2. "공유" 버튼 클릭
3. 서비스 계정 이메일 주소 추가 (편집 권한)
4. 이메일 형식: `your-service-account@your-project.iam.gserviceaccount.com`
5. "완료" 클릭

#### ❌ 문제 3: "스프레드시트 ID가 올바르지 않습니다"

**해결방법:**

1. Google Sheets URL에서 ID 추출
2. URL 형식: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
3. `config.py`에서 `SPREADSHEET_ID` 값 확인
4. 올바른 ID로 수정

#### ❌ 문제 4: "Google Sheets API가 활성화되지 않았습니다"

**해결방법:**

1. Google Cloud Console 접속
2. "API 및 서비스" > "라이브러리" 이동
3. "Google Sheets API" 검색
4. "사용" 버튼 클릭하여 활성화

### 3️⃣ 단계별 설정 확인

#### 단계 1: 파일 구조 확인

```
프로젝트 폴더/
├── credentials.json          ← Google 서비스 계정 키
├── config.py                ← 설정 파일
├── main_with_sheets_fix.py  ← 문제 해결된 메인 프로그램
├── test_sheets_connection.py ← 연결 테스트
└── run_with_sheets_fix.bat  ← 실행 스크립트
```

#### 단계 2: config.py 설정 확인

```python
# config.py 파일 내용 확인
GOOGLE_CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = '1B001qtMZKIEv_1DGCdwidNuiYI4-QLBZNzR5EpwyoKg'  # 올바른 ID인지 확인
WORKSHEET_NAME = '교육 뉴스 크롤링'
```

#### 단계 3: credentials.json 파일 확인

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

### 4️⃣ 문제 해결된 프로그램 사용법

#### A. 기본 실행

```bash
# Windows
run_with_sheets_fix.bat

# 또는 직접 실행
python main_with_sheets_fix.py
```

#### B. 연결 테스트만 실행

```bash
python test_sheets_connection.py
```

#### C. 상세 진단 실행

```bash
python diagnose_sheets.py
```

### 5️⃣ 문제 해결된 프로그램의 특징

#### ✅ 개선된 기능들

1. **자동 연결 확인**: 프로그램 시작 시 Google Sheets 연결 상태 확인
2. **상세한 오류 메시지**: 문제 발생 시 구체적인 해결 방법 제시
3. **대체 저장 방식**: Google Sheets 연결 실패 시 JSON 파일로 저장
4. **연결 테스트**: 실제 데이터 읽기/쓰기 테스트 수행
5. **워크시트 자동 생성**: 필요한 워크시트 자동 생성

#### 🔧 문제 해결 로직

```python
# 1. 자격 증명 파일 확인
if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
    print("❌ 자격 증명 파일이 없습니다!")
    return False

# 2. Google Sheets 연결 테스트
try:
    sheets_manager = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, SPREADSHEET_ID)
    worksheets = sheets_manager.get_worksheets()
    print("✅ Google Sheets 연결 성공!")
except Exception as e:
    print(f"❌ 연결 실패: {e}")
    print("💡 해결 방법 제시")
    return False

# 3. 워크시트 확인 및 생성
if not target_worksheet:
    print("⚠️ 워크시트가 없습니다. 생성 중...")
    sheets_manager.create_worksheet(WORKSHEET_NAME)
```

### 6️⃣ 로그 파일 확인

#### 로그 파일 위치

- `education_news_crawler.log` - 일반 로그
- `crawler_errors.log` - 에러 로그
- `performance_metrics.json` - 성능 메트릭

#### 로그에서 확인할 내용

```
✅ Google Sheets 연결 성공!
✅ 대상 워크시트 '교육 뉴스 크롤링' 확인
✅ 헤더 설정 완료
✅ 구글 스프레드시트에 5개 뉴스 업로드 완료
```

### 7️⃣ 추가 도구들

#### A. 진단 도구 (`diagnose_sheets.py`)

- 설정 파일 확인
- 자격 증명 파일 검증
- Google Sheets 연결 테스트
- 데이터 읽기/쓰기 테스트
- 일반적인 문제 해결 방법 제시

#### B. 연결 테스트 (`test_sheets_connection.py`)

- 빠른 연결 테스트
- 설정 확인
- 기본적인 문제 진단

#### C. 문제 해결된 메인 프로그램 (`main_with_sheets_fix.py`)

- 자동 연결 확인
- 상세한 오류 메시지
- 대체 저장 방식
- 워크시트 자동 생성

### 8️⃣ 문제가 계속 발생하는 경우

#### 체크리스트

- [ ] `credentials.json` 파일이 프로젝트 폴더에 있는가?
- [ ] Google Sheets에서 서비스 계정 이메일로 공유했는가?
- [ ] Google Sheets API가 활성화되어 있는가?
- [ ] 스프레드시트 ID가 올바른가?
- [ ] 워크시트 이름이 정확한가?
- [ ] 인터넷 연결이 정상적인가?

#### 추가 확인사항

1. **방화벽 설정**: 회사 네트워크에서 Google API 접근 차단 가능
2. **권한 설정**: 서비스 계정에 충분한 권한이 있는지 확인
3. **API 할당량**: Google API 할당량 초과 여부 확인
4. **계정 상태**: Google 계정이 정상 상태인지 확인

### 9️⃣ 성공 확인 방법

#### A. 로그 확인

```
✅ Google Sheets 연결 성공!
✅ 구글 스프레드시트에 5개 뉴스 업로드 완료
```

#### B. Google Sheets 확인

1. Google Sheets에서 스프레드시트 열기
2. "교육 뉴스 크롤링" 워크시트 확인
3. 새로운 뉴스 데이터가 추가되었는지 확인

#### C. JSON 파일 확인

- `education_news.json` 파일에 뉴스 데이터 저장 확인
- Google Sheets 연결 실패 시에도 데이터 보존

### 🔟 문제 해결 완료 후

#### 정상 작동 확인

```bash
# 1. 연결 테스트
python test_sheets_connection.py

# 2. 크롤링 실행
python main_with_sheets_fix.py

# 3. 결과 확인
# - Google Sheets에서 데이터 확인
# - 로그 파일에서 성공 메시지 확인
```

이제 Google Sheets 연동 문제가 해결되었습니다! 🎉
