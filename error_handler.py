# 에러 처리 및 로깅 모듈
import logging
import traceback
import functools
from datetime import datetime
from typing import Any, Callable, Optional
import json
import os

class ErrorHandler:
    """통합 에러 처리 및 로깅 클래스"""
    
    def __init__(self, log_file: str = 'crawler_errors.log'):
        self.log_file = log_file
        self.setup_logging()
        self.error_stats = {
            'network_errors': 0,
            'parsing_errors': 0,
            'timeout_errors': 0,
            'authentication_errors': 0,
            'total_errors': 0
        }
    
    def setup_logging(self):
        """로깅 설정"""
        # 에러 전용 로거
        self.error_logger = logging.getLogger('crawler_errors')
        self.error_logger.setLevel(logging.ERROR)
        
        # 파일 핸들러
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.ERROR)
        
        # 포맷터
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # 핸들러 추가
        if not self.error_logger.handlers:
            self.error_logger.addHandler(file_handler)
    
    def handle_error(self, error: Exception, context: str = "", 
                    source: str = "", url: str = "") -> dict:
        """에러 처리 및 분류"""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'source': source,
            'url': url,
            'traceback': traceback.format_exc()
        }
        
        # 에러 타입별 분류
        if isinstance(error, (ConnectionError, TimeoutError)):
            self.error_stats['network_errors'] += 1
            error_info['category'] = 'network'
        elif isinstance(error, (AttributeError, KeyError, ValueError)):
            self.error_stats['parsing_errors'] += 1
            error_info['category'] = 'parsing'
        elif isinstance(error, TimeoutError):
            self.error_stats['timeout_errors'] += 1
            error_info['category'] = 'timeout'
        elif 'auth' in str(error).lower() or 'credential' in str(error).lower():
            self.error_stats['authentication_errors'] += 1
            error_info['category'] = 'authentication'
        else:
            error_info['category'] = 'unknown'
        
        self.error_stats['total_errors'] += 1
        
        # 로그 기록
        self.error_logger.error(f"[{error_info['category'].upper()}] {context}: {error}")
        
        return error_info
    
    def retry_on_error(self, max_retries: int = 3, delay: float = 1.0):
        """에러 발생 시 재시도 데코레이터"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_error = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_error = e
                        if attempt < max_retries:
                            self.error_logger.warning(
                                f"재시도 {attempt + 1}/{max_retries}: {func.__name__} - {e}"
                            )
                            import time
                            time.sleep(delay * (2 ** attempt))  # 지수 백오프
                        else:
                            self.handle_error(
                                e, 
                                f"최대 재시도 횟수 초과: {func.__name__}",
                                source=getattr(args[0], '__class__', {}).get('__name__', 'Unknown'),
                                url=getattr(kwargs, 'url', '')
                            )
                
                raise last_error
            return wrapper
        return decorator
    
    def safe_execute(self, func: Callable, *args, **kwargs) -> tuple[Any, bool]:
        """안전한 함수 실행"""
        try:
            result = func(*args, **kwargs)
            return result, True
        except Exception as e:
            error_info = self.handle_error(
                e, 
                f"함수 실행 실패: {func.__name__}",
                source=getattr(args[0], '__class__', {}).get('__name__', 'Unknown') if args else 'Unknown'
            )
            return None, False
    
    def get_error_stats(self) -> dict:
        """에러 통계 반환"""
        return self.error_stats.copy()
    
    def save_error_report(self, filename: str = 'error_report.json'):
        """에러 리포트 저장"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'error_stats': self.error_stats,
            'log_file': self.log_file
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.error_logger.error(f"에러 리포트 저장 실패: {e}")

# 전역 에러 핸들러 인스턴스
error_handler = ErrorHandler()

def log_performance(func: Callable) -> Callable:
    """성능 로깅 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logging.info(f"✅ {func.__name__} 완료 - 소요시간: {execution_time:.2f}초")
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logging.error(f"❌ {func.__name__} 실패 - 소요시간: {execution_time:.2f}초 - 오류: {e}")
            raise
    return wrapper
