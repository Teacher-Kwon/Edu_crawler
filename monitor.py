# 모니터링 및 알림 시스템
import logging
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from dataclasses import dataclass
from typing import Any

@dataclass
class AlertThreshold:
    """알림 임계값 설정"""
    max_errors_per_hour: int = 10
    max_response_time: float = 30.0  # 초
    min_success_rate: float = 0.8  # 80%
    max_memory_usage: float = 0.9  # 90%

class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self, config_file: str = 'monitor_config.json'):
        self.config_file = config_file
        self.metrics = {
            'crawl_sessions': [],
            'error_logs': [],
            'performance_data': []
        }
        self.thresholds = AlertThreshold()
        self.load_config()
    
    def load_config(self):
        """설정 파일 로드"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.thresholds = AlertThreshold(**config.get('thresholds', {}))
            except Exception as e:
                logging.warning(f"모니터링 설정 로드 실패: {e}")
    
    def record_crawl_session(self, source: str, news_count: int, 
                           duration: float, success: bool, errors: List[str] = None):
        """크롤링 세션 기록"""
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'news_count': news_count,
            'duration': duration,
            'success': success,
            'errors': errors or []
        }
        
        self.metrics['crawl_sessions'].append(session_data)
        
        # 최근 24시간 데이터만 유지
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.metrics['crawl_sessions'] = [
            session for session in self.metrics['crawl_sessions']
            if datetime.fromisoformat(session['timestamp']) > cutoff_time
        ]
    
    def record_error(self, error_type: str, message: str, source: str = ""):
        """에러 기록"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'message': message,
            'source': source
        }
        
        self.metrics['error_logs'].append(error_data)
        
        # 최근 24시간 데이터만 유지
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.metrics['error_logs'] = [
            error for error in self.metrics['error_logs']
            if datetime.fromisoformat(error['timestamp']) > cutoff_time
        ]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 정보"""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)
        
        # 최근 1시간 에러 수
        recent_errors = [
            error for error in self.metrics['error_logs']
            if datetime.fromisoformat(error['timestamp']) > last_hour
        ]
        
        # 최근 24시간 세션 통계
        recent_sessions = [
            session for session in self.metrics['crawl_sessions']
            if datetime.fromisoformat(session['timestamp']) > last_24h
        ]
        
        if not recent_sessions:
            return {
                'status': 'no_data',
                'message': '최근 24시간 동안 크롤링 데이터가 없습니다.'
            }
        
        # 성공률 계산
        successful_sessions = [s for s in recent_sessions if s['success']]
        success_rate = len(successful_sessions) / len(recent_sessions) if recent_sessions else 0
        
        # 평균 응답 시간
        avg_duration = sum(s['duration'] for s in recent_sessions) / len(recent_sessions)
        
        # 총 뉴스 수집 수
        total_news = sum(s['news_count'] for s in recent_sessions)
        
        return {
            'status': 'healthy' if self._is_healthy(success_rate, len(recent_errors), avg_duration) else 'warning',
            'success_rate': success_rate,
            'avg_response_time': avg_duration,
            'total_news_collected': total_news,
            'recent_errors': len(recent_errors),
            'sessions_count': len(recent_sessions),
            'last_update': now.isoformat()
        }
    
    def _is_healthy(self, success_rate: float, error_count: int, avg_duration: float) -> bool:
        """시스템 상태 판단"""
        return (
            success_rate >= self.thresholds.min_success_rate and
            error_count <= self.thresholds.max_errors_per_hour and
            avg_duration <= self.thresholds.max_response_time
        )
    
    def check_alerts(self) -> List[Dict[str, str]]:
        """알림 확인"""
        alerts = []
        summary = self.get_performance_summary()
        
        if summary['status'] != 'healthy':
            if summary['success_rate'] < self.thresholds.min_success_rate:
                alerts.append({
                    'type': 'low_success_rate',
                    'message': f"성공률이 낮습니다: {summary['success_rate']:.1%}",
                    'severity': 'warning'
                })
            
            if summary['recent_errors'] > self.thresholds.max_errors_per_hour:
                alerts.append({
                    'type': 'high_error_rate',
                    'message': f"에러 발생률이 높습니다: {summary['recent_errors']}개/시간",
                    'severity': 'critical'
                })
            
            if summary['avg_response_time'] > self.thresholds.max_response_time:
                alerts.append({
                    'type': 'slow_response',
                    'message': f"응답 시간이 느립니다: {summary['avg_response_time']:.1f}초",
                    'severity': 'warning'
                })
        
        return alerts
    
    def save_metrics(self, filename: str = 'performance_metrics.json'):
        """메트릭 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"메트릭 저장 실패: {e}")

class NotificationManager:
    """알림 관리 클래스"""
    
    def __init__(self, email_config: Optional[Dict] = None):
        self.email_config = email_config or {}
        self.notification_history = []
    
    def send_email_alert(self, subject: str, message: str, recipients: List[str]):
        """이메일 알림 전송"""
        if not self.email_config.get('enabled', False):
            logging.info("이메일 알림이 비활성화되어 있습니다.")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['sender_email'], recipients, text)
            server.quit()
            
            logging.info(f"이메일 알림 전송 완료: {subject}")
            return True
            
        except Exception as e:
            logging.error(f"이메일 알림 전송 실패: {e}")
            return False
    
    def send_console_alert(self, message: str, severity: str = 'info'):
        """콘솔 알림"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if severity == 'critical':
            print(f"🚨 [{timestamp}] CRITICAL: {message}")
        elif severity == 'warning':
            print(f"⚠️ [{timestamp}] WARNING: {message}")
        else:
            print(f"ℹ️ [{timestamp}] INFO: {message}")
    
    def log_notification(self, message: str, severity: str = 'info'):
        """알림 기록"""
        notification = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'severity': severity
        }
        
        self.notification_history.append(notification)
        
        # 최근 100개 알림만 유지
        if len(self.notification_history) > 100:
            self.notification_history = self.notification_history[-100:]

# 전역 모니터링 인스턴스
performance_monitor = PerformanceMonitor()
notification_manager = NotificationManager()

def monitor_crawl_performance(func):
    """크롤링 성능 모니터링 데코레이터"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        source_name = getattr(args[0], '__class__', {}).get('__name__', 'Unknown')
        
        try:
            result = func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            
            # 성공 기록
            news_count = len(result) if isinstance(result, list) else 0
            performance_monitor.record_crawl_session(
                source=source_name,
                news_count=news_count,
                duration=duration,
                success=True
            )
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            
            # 실패 기록
            performance_monitor.record_crawl_session(
                source=source_name,
                news_count=0,
                duration=duration,
                success=False,
                errors=[str(e)]
            )
            
            # 에러 기록
            performance_monitor.record_error(
                error_type=type(e).__name__,
                message=str(e),
                source=source_name
            )
            
            raise
    
    return wrapper
