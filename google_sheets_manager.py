# 구글 스프레드시트 관리 모듈
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    def __init__(self, credentials_file, spreadsheet_id):
        """
        구글 스프레드시트 매니저 초기화
        
        Args:
            credentials_file (str): 구글 서비스 계정 키 파일 경로
            spreadsheet_id (str): 구글 스프레드시트 ID
        """
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """구글 API 인증"""
        try:
            # 서비스 계정 인증
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=scopes
            )
            
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("구글 스프레드시트 API 인증 성공")
            
        except Exception as e:
            logger.error(f"구글 API 인증 실패: {e}")
            raise
    
    def get_worksheet_data(self, worksheet_name, range_name=None):
        """워크시트 데이터 읽기"""
        try:
            if range_name is None:
                range_name = f"{worksheet_name}!A:Z"
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            return values
            
        except HttpError as e:
            logger.error(f"워크시트 데이터 읽기 실패: {e}")
            return []
    
    def append_data(self, worksheet_name, data):
        """워크시트에 데이터 추가"""
        try:
            # 데이터를 2차원 리스트로 변환
            if isinstance(data, pd.DataFrame):
                values = [data.columns.tolist()] + data.values.tolist()
                logger.info(f"📊 DataFrame 컬럼 수: {len(data.columns)}")
                logger.info(f"📊 DataFrame 행 수: {len(data)}")
            elif isinstance(data, list):
                values = data
            else:
                raise ValueError("지원하지 않는 데이터 타입입니다.")
            
            # 컬럼 수 검증
            if len(values) > 0:
                header_columns = len(values[0]) if values[0] else 0
                data_columns = len(values[1]) if len(values) > 1 else 0
                logger.info(f"📊 헤더 컬럼 수: {header_columns}, 데이터 컬럼 수: {data_columns}")
                
                if header_columns != data_columns and len(values) > 1:
                    logger.error(f"❌ 컬럼 수 불일치: 헤더 {header_columns}개, 데이터 {data_columns}개")
                    return False
            
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{worksheet_name}!A:Z",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            logger.info(f"데이터 추가 완료: {result.get('updates', {}).get('updatedRows', 0)}행")
            return True
            
        except HttpError as e:
            logger.error(f"데이터 추가 실패: {e}")
            return False
    
    def replace_worksheet_data(self, worksheet_name, df):
        """워크시트 전체 데이터 교체 (헤더 + 데이터)"""
        try:
            # DataFrame을 리스트로 변환 (헤더 포함)
            values = [df.columns.tolist()] + df.values.tolist()
            
            # 전체 범위 교체
            body = {'values': values}
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{worksheet_name}!A:Z",
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"워크시트 '{worksheet_name}' 전체 데이터 교체 완료 ({len(df)}개 행)")
            return True
            
        except HttpError as e:
            logger.error(f"워크시트 데이터 교체 실패: {e}")
            return False
        except Exception as e:
            logger.error(f"워크시트 데이터 교체 중 오류 발생: {e}")
            return False
    
    def update_data(self, worksheet_name, data, start_row=1):
        """워크시트 데이터 업데이트"""
        try:
            if isinstance(data, pd.DataFrame):
                values = [data.columns.tolist()] + data.values.tolist()
            elif isinstance(data, list):
                values = data
            else:
                raise ValueError("지원하지 않는 데이터 타입입니다.")
            
            # 기존 데이터가 있는지 확인
            existing_data = self.get_worksheet_data(worksheet_name)
            
            if not existing_data:
                # 헤더만 있는 경우
                range_name = f"{worksheet_name}!A1"
            else:
                # 기존 데이터가 있는 경우 마지막 행 다음부터
                range_name = f"{worksheet_name}!A{len(existing_data) + 1}"
            
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"데이터 업데이트 완료: {result.get('updatedRows', 0)}행")
            return True
            
        except HttpError as e:
            logger.error(f"데이터 업데이트 실패: {e}")
            return False
    
    def clear_worksheet(self, worksheet_name):
        """워크시트 데이터 전체 삭제"""
        try:
            result = self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=f"{worksheet_name}!A:Z"
            ).execute()
            
            logger.info("워크시트 데이터 삭제 완료")
            return True
            
        except HttpError as e:
            logger.error(f"워크시트 데이터 삭제 실패: {e}")
            return False
    
    def create_worksheet(self, worksheet_name):
        """새 워크시트 생성"""
        try:
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': worksheet_name
                        }
                    }
                }]
            }
            
            result = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=request_body
            ).execute()
            
            logger.info(f"워크시트 생성 완료: {worksheet_name}")
            return True
            
        except HttpError as e:
            if "already exists" in str(e):
                logger.info(f"워크시트가 이미 존재합니다: {worksheet_name}")
                return True
            else:
                logger.error(f"워크시트 생성 실패: {e}")
                return False
    
    def get_worksheets(self):
        """스프레드시트의 모든 워크시트 정보 가져오기"""
        try:
            result = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            worksheets = result.get('sheets', [])
            logger.info(f"워크시트 수: {len(worksheets)}")
            return worksheets
            
        except HttpError as e:
            logger.error(f"워크시트 정보 가져오기 실패: {e}")
            return []
    
    def setup_headers(self, worksheet_name, headers):
        """워크시트 헤더 설정"""
        try:
            body = {
                'values': [headers]
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{worksheet_name}!A1",
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info("헤더 설정 완료")
            return True
            
        except HttpError as e:
            logger.error(f"헤더 설정 실패: {e}")
            return False

if __name__ == "__main__":
    from config import GOOGLE_CREDENTIALS_FILE, SPREADSHEET_ID, WORKSHEET_NAME, COLUMNS
    
    # 테스트용
    if SPREADSHEET_ID:
        manager = GoogleSheetsManager(GOOGLE_CREDENTIALS_FILE, SPREADSHEET_ID)
        
        # 워크시트 생성
        manager.create_worksheet(WORKSHEET_NAME)
        
        # 헤더 설정
        manager.setup_headers(WORKSHEET_NAME, COLUMNS)
        
        print("구글 스프레드시트 설정 완료")
    else:
        print("config.py에서 SPREADSHEET_ID를 설정해주세요.")
