# 🚀 GitHub Actions 자동 크롤링 설정 가이드

## 📋 개요

GitHub Actions를 통해 1시간마다 자동으로 교육 뉴스를 크롤링하고 Google Sheets에 업로드하는 설정 방법입니다.

## ⚙️ 설정 방법

### 1️⃣ GitHub Repository 설정

#### A. Repository 생성 또는 기존 Repository 사용

1. GitHub에서 새 Repository 생성
2. 프로젝트 파일들을 Repository에 업로드
3. Repository를 Public 또는 Private으로 설정

#### B. Secrets 설정 (중요!)

Repository Settings > Secrets and variables > Actions에서 다음 Secrets 추가:

```
GOOGLE_CREDENTIALS_JSON
```

- **값**: `credentials.json` 파일의 전체 내용 (JSON 형식)
- **설명**: Google 서비스 계정 인증 정보

```
SPREADSHEET_ID
```

- **값**: Google Sheets 스프레드시트 ID
- **설명**: 뉴스 데이터를 업로드할 스프레드시트 ID

### 2️⃣ Google Sheets 설정

#### A. Google Cloud Console 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 선택 또는 새 프로젝트 생성
3. "API 및 서비스" > "라이브러리"에서 "Google Sheets API" 활성화
4. "API 및 서비스" > "사용자 인증 정보"에서 서비스 계정 생성
5. 서비스 계정 키 다운로드 (JSON 형식)

#### B. Google Sheets 공유 설정

1. Google Sheets에서 스프레드시트 열기
2. "공유" 버튼 클릭
3. 서비스 계정 이메일 주소 추가 (편집 권한)
4. 이메일 형식: `your-service-account@your-project.iam.gserviceaccount.com`

### 3️⃣ GitHub Actions 워크플로우 확인

#### A. 워크플로우 파일 위치

```
.github/workflows/crawl-news.yml
```

#### B. 실행 스케줄

```yaml
on:
  schedule:
    # 매시간 정시에 실행 (한국시간)
    - cron: "0 * * * *" # UTC 기준 (한국시간 -9시간)
  workflow_dispatch: # 수동 실행 가능
```

#### C. 실행 시간 설정

- **현재 설정**: 매시간 정시 (00분)
- **한국시간**: 매시간 00분
- **UTC 시간**: 매시간 00분 (한국시간 -9시간)

### 4️⃣ 수동 실행 방법

#### A. GitHub에서 수동 실행

1. Repository > Actions 탭
2. "교육 뉴스 크롤링" 워크플로우 선택
3. "Run workflow" 버튼 클릭
4. 실행 결과 확인

#### B. 로컬에서 테스트

```bash
# 로컬에서 테스트 실행
python main_final.py
```

## 📊 실행 결과 확인

### 1️⃣ GitHub Actions 로그 확인

1. Repository > Actions 탭
2. 최근 실행된 워크플로우 클릭
3. "crawl-news" 작업 클릭
4. 각 단계별 실행 로그 확인

### 2️⃣ Google Sheets 확인

1. Google Sheets에서 스프레드시트 열기
2. "교육 뉴스 크롤링" 워크시트 확인
3. 새로운 뉴스 데이터가 추가되었는지 확인
4. 최신 뉴스가 맨 위에 있는지 확인

### 3️⃣ 로그 파일 확인

GitHub Actions 실행 후 생성되는 파일들:

- `education_news_crawler.log`: 일반 실행 로그
- `crawler_errors.log`: 에러 로그
- `education_news.json`: 크롤링된 뉴스 데이터

## 🔧 문제 해결

### 1️⃣ GitHub Actions 실행 실패

#### A. Secrets 설정 확인

```
❌ GOOGLE_CREDENTIALS_JSON이 설정되지 않았습니다.
💡 Repository Settings > Secrets에서 설정 확인
```

#### B. Google Sheets 권한 확인

```
❌ Google Sheets 접근 권한이 없습니다.
💡 서비스 계정 이메일로 스프레드시트 공유 확인
```

#### C. API 할당량 확인

```
❌ Google Sheets API 할당량 초과
💡 Google Cloud Console에서 할당량 확인
```

### 2️⃣ 크롤링 실패

#### A. 네트워크 문제

```
❌ 뉴스 사이트 접근 실패
💡 GitHub Actions 로그에서 구체적인 오류 확인
```

#### B. 파싱 오류

```
❌ 뉴스 사이트 구조 변경
💡 news_crawler.py에서 파싱 로직 수정 필요
```

### 3️⃣ 데이터 중복 문제

#### A. 헤더 중복

```
❌ 스프레드시트에 헤더가 중복으로 나타남
💡 이미 해결됨: 헤더 중복 방지 로직 추가
```

#### B. 뉴스 중복

```
❌ 같은 뉴스가 여러 번 추가됨
💡 중복 제거 로직이 작동 중
```

## 📈 성능 모니터링

### 1️⃣ 실행 통계

- **성공률**: 크롤링 성공 비율
- **응답시간**: 평균 크롤링 시간
- **수집량**: 일일 뉴스 수집 수
- **에러율**: 시간당 에러 발생 수

### 2️⃣ 알림 설정

- **성공률 80% 미만**: 경고 알림
- **에러율 10개/시간 초과**: 위험 알림
- **응답시간 30초 초과**: 성능 경고

## 🔄 스케줄 변경

### 1️⃣ 실행 빈도 변경

```yaml
# 현재: 매시간
- cron: "0 * * * *"

# 30분마다
- cron: "0,30 * * * *"

# 2시간마다
- cron: "0 */2 * * * *"

# 매일 오전 9시
- cron: "0 9 * * *"
```

### 2️⃣ 시간대 변경

```yaml
# 한국시간 오전 9시 (UTC 0시)
- cron: "0 0 * * *"

# 한국시간 오후 6시 (UTC 9시)
- cron: "0 9 * * *"
```

## 📚 추가 설정

### 1️⃣ 환경변수 추가

```yaml
- name: 환경변수 설정
  run: |
    echo "CRAWL_INTERVAL=60" >> $GITHUB_ENV
    echo "MAX_NEWS_PER_SOURCE=20" >> $GITHUB_ENV
```

### 2️⃣ 알림 설정

```yaml
- name: 알림 전송
  if: failure()
  run: |
    echo "❌ 크롤링 실패 알림"
    # 이메일 또는 슬랙 알림 추가 가능
```

## 🎯 최종 확인사항

### ✅ 설정 완료 체크리스트

- [ ] GitHub Repository 생성
- [ ] Secrets 설정 (GOOGLE_CREDENTIALS_JSON, SPREADSHEET_ID)
- [ ] Google Sheets API 활성화
- [ ] 서비스 계정 권한 설정
- [ ] 워크플로우 파일 확인
- [ ] 수동 실행 테스트
- [ ] 자동 실행 확인

### 🚀 실행 결과 예시

```
🔄 크롤링 시작: 2024-01-15 09:00:00
🔍 Google Sheets 연동 확인 중...
✅ Google Sheets 연결 성공!
🚀 교육 뉴스 크롤링 시작...
📊 새로 수집된 뉴스: 15개
🔄 중복 제거 후 새 뉴스: 12개
📤 Google Sheets 업로드 시작...
✅ 구글 스프레드시트에 12개 뉴스 업로드 완료
✅ Google Sheets 업로드 완료!
⏱️ 크롤링 완료 (소요시간: 18.5초)
✅ 교육 뉴스 크롤링 및 저장 완료
```

이제 GitHub Actions를 통해 1시간마다 자동으로 교육 뉴스를 크롤링하고 Google Sheets에 업로드할 수 있습니다! 🎉
