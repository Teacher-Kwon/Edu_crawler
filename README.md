# 🚀 최종 통합된 교육 뉴스 크롤링 프로그램

## 📋 프로그램 개요

교육 관련 뉴스를 자동으로 수집하고 Google Sheets에 업로드하는 통합 프로그램입니다.

## ✨ 주요 기능

### 🔍 뉴스 크롤링

- **다중 소스 지원**: 한국교육신문, 교육희망, 교육언론창
- **병렬 처리**: 여러 소스 동시 크롤링으로 속도 향상
- **스마트 필터링**: 관련성 높은 뉴스만 선별
- **중복 제거**: 해시 기반 정확한 중복 제거

### 📊 데이터 관리

- **Google Sheets 연동**: 자동 업로드 및 동기화
- **JSON 백업**: 로컬 파일로 데이터 보존
- **데이터 검증**: 품질 검사 및 필터링

### 🛠️ 고급 기능

- **에러 처리**: 자동 재시도 및 복구
- **성능 모니터링**: 실시간 성능 지표 추적
- **알림 시스템**: 문제 발생 시 즉시 알림
- **로깅**: 상세한 실행 로그 기록

## 🚀 빠른 시작

### 1. 프로그램 실행

```bash
# Windows
run_final.bat

# 또는 직접 실행
python main_final.py
```

### 2. Google Sheets 설정 (선택사항)

1. Google Cloud Console에서 서비스 계정 생성
2. `credentials.json` 파일을 프로젝트 폴더에 저장
3. Google Sheets에서 서비스 계정 이메일로 공유
4. 자세한 설정 방법: `SHEETS_CONNECTION_GUIDE.md` 참조

## 📁 파일 구조

### 핵심 파일들

```
프로젝트 폴더/
├── main_final.py              # 🚀 메인 프로그램
├── run_final.bat             # 🚀 실행 스크립트
├── news_crawler.py           # 크롤링 엔진
├── google_sheets_manager.py  # Google Sheets 연동
├── smart_filter.py           # 스마트 필터링
├── error_handler.py          # 에러 처리
├── monitor.py                # 성능 모니터링
├── config.py                 # 설정 파일
└── requirements.txt          # 의존성 목록
```

### 문서 파일들

```
├── README.md                 # 사용법 가이드
└── SHEETS_CONNECTION_GUIDE.md # Google Sheets 연동 가이드
```

### 자동 생성 파일들

```
├── existing_news.json        # 기존 뉴스 데이터 (자동 생성)
├── education_news.json       # 크롤링된 뉴스 데이터 (자동 생성)
├── education_news_crawler.log # 실행 로그 (자동 생성)
└── crawler_errors.log        # 에러 로그 (자동 생성)
```

## ⚙️ 설정 방법

### 1. 기본 설정 (config.py)

```python
# Google Sheets 설정
GOOGLE_CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = 'your_spreadsheet_id'
WORKSHEET_NAME = '교육 뉴스 크롤링'

# 뉴스 소스 설정
NEWS_SOURCES = [
    {
        'name': '한국교육신문',
        'url': 'https://www.hangyo.com/news/articleList.html?sc_section_code=S1N1&view_type=sm',
        'base_url': 'https://www.hangyo.com'
    },
    # ... 더 많은 소스
]
```

## 📊 사용법

### 기본 실행

```bash
# Windows
run_final.bat

# 또는 직접 실행
python main_final.py
```

### 실행 결과

```
🎯 최종 통합된 교육 뉴스 크롤링 프로그램
==================================================
🔍 Google Sheets 연동 확인 중...
✅ Google Sheets 연결 성공! (워크시트 수: 1)
✅ 대상 워크시트 '교육 뉴스 크롤링' 확인
🚀 교육 뉴스 크롤링 시작...
📊 새로 수집된 뉴스: 15개
🔄 중복 제거 후 새 뉴스: 12개
📤 Google Sheets 업로드 시작...
✅ 구글 스프레드시트에 12개 뉴스 업로드 완료
✅ Google Sheets 업로드 완료!
⏱️ 크롤링 완료 (소요시간: 18.5초)
✅ 교육 뉴스 크롤링 및 저장 완료
```

## 🛠️ 문제 해결

### 일반적인 문제들

#### 1. Google Sheets 연결 실패

**해결방법**: `SHEETS_CONNECTION_GUIDE.md` 파일 참조

#### 2. 크롤링 실패

**해결방법**:

- 네트워크 연결 확인
- 뉴스 사이트 접근 가능성 확인
- 타임아웃 설정 조정

### 로그 파일 확인

- `education_news_crawler.log`: 일반 실행 로그
- `crawler_errors.log`: 에러 상세 로그
- `performance_metrics.json`: 성능 통계

## 🤖 자동 크롤링 설정 (GitHub Actions)

### 1시간마다 자동 실행

```yaml
# .github/workflows/crawl-news.yml
on:
  schedule:
    - cron: "0 * * * *" # 매시간 정시 실행
  workflow_dispatch: # 수동 실행 가능
```

### 설정 방법

1. **GitHub Repository 생성**
2. **Secrets 설정**:
   - `GOOGLE_CREDENTIALS_JSON`: Google 서비스 계정 JSON
   - `SPREADSHEET_ID`: Google Sheets 스프레드시트 ID
3. **자동 실행 확인**

자세한 설정 방법: `GITHUB_ACTIONS_SETUP.md` 참조

## 📚 추가 문서

- `GITHUB_ACTIONS_SETUP.md`: GitHub Actions 자동 크롤링 설정 가이드
- `SHEETS_CONNECTION_GUIDE.md`: Google Sheets 연동 가이드
- `requirements.txt`: 필요한 Python 패키지 목록

## 🔄 업데이트 내역

### v2.0 (최종 통합 버전)

- ✅ 모든 기능 통합
- ✅ 중복 파일 정리
- ✅ 성능 최적화
- ✅ 에러 처리 강화
- ✅ 모니터링 시스템 추가

## 📞 지원

문제가 발생하면 다음을 확인해주세요:

1. 로그 파일 확인
2. 설정 파일 유효성 검사
3. 의존성 버전 확인
4. Google Sheets 연결 상태 확인
