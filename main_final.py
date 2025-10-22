# 🚀 최종 통합된 교육 뉴스 크롤링 프로그램
import logging
import sys
import os
import json
from datetime import datetime
from typing import List, Dict

# 핵심 모듈들 import
from news_crawler import EducationNewsCrawler
from google_sheets_manager import GoogleSheetsManager
from config import (
    NEWS_SOURCES, 
    GOOGLE_CREDENTIALS_FILE, 
    SPREADSHEET_ID, 
    WORKSHEET_NAME, 
    COLUMNS
)
from error_handler import error_handler
from monitor import performance_monitor, notification_manager

# 로깅 설정
def setup_logging():
    """로깅 설정"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 파일 핸들러
    file_handler = logging.FileHandler('education_news_crawler.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # 루트 로거 설정
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[file_handler, console_handler]
    )

class FinalEducationNewsManager:
    """최종 통합된 교육 뉴스 관리자"""
    
    def __init__(self):
        """초기화"""
        self.crawler = EducationNewsCrawler()
        self.sheets_manager = None
        self.existing_news_file = 'existing_news.json'
        self.existing_news = self.load_existing_news()
        
        # Google Sheets 초기화
        self.initialize_google_sheets()
    
    def initialize_google_sheets(self):
        """Google Sheets 초기화 (통합된 버전)"""
        print("🔍 Google Sheets 연동 확인 중...")
        
        # 1. 자격 증명 파일 확인
        if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
            print(f"❌ 자격 증명 파일이 없습니다: {GOOGLE_CREDENTIALS_FILE}")
            print("💡 Google Cloud Console에서 서비스 계정을 생성하고 키 파일을 다운로드하세요.")
            print("   📋 자세한 설정 방법: SHEETS_CONNECTION_GUIDE.md 파일 참조")
            return False
        
        # 2. 스프레드시트 ID 확인
        if not SPREADSHEET_ID:
            print("❌ 스프레드시트 ID가 설정되지 않았습니다.")
            print("💡 config.py에서 SPREADSHEET_ID를 설정해주세요.")
            return False
        
        # 3. Google Sheets 연결 시도
        try:
            print("🔄 Google Sheets 연결 시도 중...")
            self.sheets_manager = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, SPREADSHEET_ID)
            
            # 연결 테스트
            worksheets = self.sheets_manager.get_worksheets()
            print(f"✅ Google Sheets 연결 성공! (워크시트 수: {len(worksheets)})")
            
            # 대상 워크시트 확인
            target_worksheet = None
            for ws in worksheets:
                if ws.title == WORKSHEET_NAME:
                    target_worksheet = ws
                    break
            
            if not target_worksheet:
                print(f"⚠️ 대상 워크시트 '{WORKSHEET_NAME}'가 없습니다.")
                print("💡 워크시트를 생성하거나 이름을 확인해주세요.")
                return False
            
            print(f"✅ 대상 워크시트 '{WORKSHEET_NAME}' 확인")
            return True
            
        except Exception as e:
            print(f"❌ Google Sheets 연결 실패: {e}")
            print("💡 다음을 확인해주세요:")
            print("   1. credentials.json 파일이 올바른지 확인")
            print("   2. Google Sheets에서 서비스 계정 이메일로 공유 설정")
            print("   3. Google Sheets API가 활성화되어 있는지 확인")
            print("   4. 스프레드시트 ID가 올바른지 확인")
            print("   📋 자세한 해결 방법: SHEETS_CONNECTION_GUIDE.md 파일 참조")
            return False
    
    def load_existing_news(self) -> List[Dict]:
        """기존 뉴스 데이터 로드"""
        if os.path.exists(self.existing_news_file):
            try:
                with open(self.existing_news_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                error_handler.handle_error(e, "기존 뉴스 로드 실패")
                return []
        return []
    
    def save_existing_news(self, news_list: List[Dict]):
        """기존 뉴스 데이터 저장"""
        try:
            with open(self.existing_news_file, 'w', encoding='utf-8') as f:
                json.dump(news_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            error_handler.handle_error(e, "기존 뉴스 저장 실패")
    
    def is_duplicate(self, new_news: Dict) -> bool:
        """중복 뉴스 체크"""
        for existing in self.existing_news:
            if (existing.get('제목') == new_news.get('제목') or 
                existing.get('링크') == new_news.get('링크')):
                return True
        return False
    
    def crawl_and_save_news(self) -> bool:
        """뉴스 크롤링 및 저장 (최종 통합 버전)"""
        try:
            print("🚀 교육 뉴스 크롤링 시작...")
            start_time = datetime.now()
            
            # 뉴스 크롤링
            new_news_list = self.crawler.crawl_all_sources(NEWS_SOURCES)
            
            if not new_news_list:
                print("⚠️ 크롤링된 뉴스가 없습니다.")
                return False
            
            print(f"📊 새로 수집된 뉴스: {len(new_news_list)}개")
            
            # 중복 제거
            unique_new_news = []
            for news in new_news_list:
                if not self.is_duplicate(news):
                    unique_new_news.append(news)
                else:
                    print(f"중복 제외: {news.get('제목', '')[:30]}...")
            
            print(f"🔄 중복 제거 후 새 뉴스: {len(unique_new_news)}개")
            
            if not unique_new_news:
                print("ℹ️ 새로운 뉴스가 없습니다.")
                return True
            
            # 기존 뉴스와 합치기
            all_news = self.existing_news + unique_new_news
            
            # 최신순으로 정렬 (최대 100개 유지)
            all_news = all_news[-100:]
            
            # 기존 뉴스 업데이트
            self.existing_news = all_news
            self.save_existing_news(all_news)
            
            # 구글 스프레드시트에 업로드
            if self.sheets_manager:
                print("📤 Google Sheets 업로드 시작...")
                success = self.upload_to_sheets(unique_new_news)
                if success:
                    print("✅ Google Sheets 업로드 완료!")
                else:
                    print("❌ Google Sheets 업로드 실패!")
            else:
                print("⚠️ Google Sheets가 연결되지 않았습니다.")
                print("💡 JSON 파일로만 저장됩니다.")
            
            # JSON 파일로도 저장 (백업)
            self.crawler.save_to_json(unique_new_news, 'education_news.json')
            
            # 성능 모니터링
            duration = (datetime.now() - start_time).total_seconds()
            performance_monitor.record_crawl_session(
                source="all_sources",
                news_count=len(unique_new_news),
                duration=duration,
                success=True
            )
            
            # 알림 확인
            alerts = performance_monitor.check_alerts()
            if alerts:
                for alert in alerts:
                    notification_manager.send_console_alert(
                        alert['message'], 
                        alert['severity']
                    )
            
            print(f"⏱️ 크롤링 완료 (소요시간: {duration:.1f}초)")
            
            return True
            
        except Exception as e:
            error_handler.handle_error(e, "뉴스 크롤링 및 저장 실패")
            return False
    
    def upload_to_sheets(self, news_list: List[Dict]) -> bool:
        """구글 스프레드시트에 데이터 업로드 (개선된 버전)"""
        try:
            if not self.sheets_manager:
                print("❌ Google Sheets 매니저가 초기화되지 않았습니다.")
                return False
            
            # 워크시트 생성 (이미 존재하면 무시)
            self.sheets_manager.create_worksheet(WORKSHEET_NAME)
            
            # 기존 데이터 가져오기
            existing_data = self.sheets_manager.get_worksheet_data(WORKSHEET_NAME)
            
            # 헤더 중복 방지: 기존 데이터가 없거나 헤더가 없을 때만 설정
            if not existing_data or len(existing_data) == 0:
                self.sheets_manager.setup_headers(WORKSHEET_NAME, COLUMNS)
                print("✅ 헤더 설정 완료")
                # 헤더 설정 후 다시 데이터 가져오기
                existing_data = self.sheets_manager.get_worksheet_data(WORKSHEET_NAME)
            
            # 데이터를 DataFrame으로 변환
            import pandas as pd
            df = pd.DataFrame(news_list)
            
            if not df.empty:
                # 중복 제거 (제목 기준)
                df = df.drop_duplicates(subset=['제목'], keep='last')
                
                # 날짜 기준으로 최신순 정렬 (새 뉴스가 맨 위에 오도록)
                if '날짜' in df.columns:
                    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
                    df = df.sort_values('날짜', ascending=False, na_position='last')
                    df['날짜'] = df['날짜'].dt.strftime('%Y-%m-%d')
                
                # 크롤링시간 정리
                if '크롤링시간' in df.columns:
                    df['크롤링시간'] = pd.to_datetime(df['크롤링시간']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
                # 기존 데이터와 합치기
                if existing_data and len(existing_data) > 1:
                    # 기존 데이터를 DataFrame으로 변환 (헤더 제외)
                    existing_df = pd.DataFrame(existing_data[1:], columns=existing_data[0])
                    
                    # 새 데이터와 기존 데이터 합치기
                    combined_df = pd.concat([df, existing_df], ignore_index=True)
                    
                    # 중복 제거 (제목 기준, 새 데이터 우선)
                    combined_df = combined_df.drop_duplicates(subset=['제목'], keep='first')
                    
                    # 날짜 기준으로 최신순 정렬 (새 뉴스가 맨 위에)
                    if '날짜' in combined_df.columns:
                        combined_df['날짜'] = pd.to_datetime(combined_df['날짜'], errors='coerce')
                        combined_df = combined_df.sort_values('날짜', ascending=False, na_position='last')
                        combined_df['날짜'] = combined_df['날짜'].dt.strftime('%Y-%m-%d')
                    
                    # 전체 워크시트 교체 (헤더 + 데이터)
                    success = self.sheets_manager.replace_worksheet_data(WORKSHEET_NAME, combined_df)
                    print(f"📊 전체 데이터 업데이트: {len(combined_df)}개 뉴스")
                else:
                    # 새 데이터만 추가
                    success = self.sheets_manager.append_data(WORKSHEET_NAME, df)
                    print(f"📊 새 데이터 추가: {len(df)}개 뉴스")
                
                if success:
                    print(f"✅ 구글 스프레드시트 업로드 완료 (최신순 정렬)")
                    return True
                else:
                    print("❌ 구글 스프레드시트 업로드 실패")
                    return False
            else:
                print("⚠️ 업로드할 뉴스 데이터가 없습니다.")
                return True
                
        except Exception as e:
            error_handler.handle_error(e, "구글 스프레드시트 업로드 실패")
            print(f"❌ 업로드 중 오류 발생: {e}")
            return False
    
    def get_system_status(self) -> Dict:
        """시스템 상태 조회"""
        return {
            'google_sheets_connected': self.sheets_manager is not None,
            'existing_news_count': len(self.existing_news),
            'performance_summary': performance_monitor.get_performance_summary(),
            'error_stats': error_handler.get_error_stats()
        }

def main():
    """메인 실행 함수"""
    setup_logging()
    print("🎯 최종 통합된 교육 뉴스 크롤링 프로그램")
    print("=" * 50)
    
    try:
        # 교육 뉴스 관리자 초기화
        manager = FinalEducationNewsManager()
        
        # 시스템 상태 출력
        status = manager.get_system_status()
        print(f"📊 시스템 상태:")
        print(f"   - Google Sheets: {'연결됨' if status['google_sheets_connected'] else '연결 안됨'}")
        print(f"   - 기존 뉴스: {status['existing_news_count']}개")
        
        # 뉴스 크롤링 및 저장
        success = manager.crawl_and_save_news()
        
        if success:
            print("✅ 교육 뉴스 크롤링 및 저장 완료")
            
            # 성능 통계 출력
            perf_stats = status['performance_summary']
            if perf_stats.get('status') != 'no_data':
                print(f"📈 성능 통계:")
                print(f"   - 성공률: {perf_stats.get('success_rate', 0):.1%}")
                print(f"   - 평균 응답시간: {perf_stats.get('avg_response_time', 0):.1f}초")
                print(f"   - 수집된 뉴스: {perf_stats.get('total_news_collected', 0)}개")
        else:
            print("❌ 교육 뉴스 크롤링 및 저장 실패")
            
    except Exception as e:
        error_handler.handle_error(e, "메인 프로그램 실행 실패")
        print(f"❌ 프로그램 실행 중 치명적 오류 발생: {e}")

if __name__ == "__main__":
    main()
