@echo off
echo ========================================
echo   최종 통합된 교육 뉴스 크롤링 프로그램
echo ========================================
echo.

REM Python 환경 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo 💡 Python 3.8 이상을 설치해주세요.
    pause
    exit /b 1
)

echo ✅ Python 환경 확인 완료

REM 가상환경 확인 및 생성
if not exist "venv" (
    echo 🔧 가상환경 생성 중...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 가상환경 생성 실패
        pause
        exit /b 1
    )
)

REM 가상환경 활성화
echo 🔄 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM 의존성 설치
echo 📦 의존성 설치 중...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 의존성 설치 실패
    pause
    exit /b 1
)

echo ✅ 의존성 설치 완료

REM Google 자격 증명 파일 확인
if not exist "credentials.json" (
    echo ⚠️ Google 자격 증명 파일이 없습니다.
    echo 💡 Google Cloud Console에서 서비스 계정을 생성하고
    echo    credentials.json 파일을 프로젝트 폴더에 저장해주세요.
    echo 📋 자세한 설정 방법: SHEETS_CONNECTION_GUIDE.md 파일 참조
    echo.
    echo 계속하려면 아무 키나 누르세요...
    pause
)

REM 최종 통합된 메인 프로그램 실행
echo 🚀 최종 통합된 교육 뉴스 크롤링 프로그램 시작...
echo.

python main_final.py

echo.
echo 📊 크롤링 완료!
echo 💡 로그 파일: education_news_crawler.log
echo 💡 에러 로그: crawler_errors.log
echo 💡 성능 메트릭: performance_metrics.json
echo.

pause
