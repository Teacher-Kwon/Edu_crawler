# 교육 뉴스 크롤링 모듈 (개선된 버전)
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
from urllib.parse import urljoin, urlparse
import logging
from smart_filter import SmartNewsFilter
from error_handler import error_handler, log_performance
import concurrent.futures
from typing import List, Dict, Optional
import hashlib

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EducationNewsCrawler:
    def __init__(self, max_workers: int = 3, timeout: int = 15):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.smart_filter = SmartNewsFilter()
        self.max_workers = max_workers
        self.timeout = timeout
        self.crawled_urls = set()  # 크롤링된 URL 캐시
        self.performance_stats = {
            'total_crawled': 0,
            'successful_crawls': 0,
            'failed_crawls': 0,
            'average_response_time': 0
        }
    
    def extract_clean_title(self, text):
        """깔끔한 제목만 추출 (원본 제목 최대한 보존)"""
        if not text:
            return ""
        
        import re
        
        # 최소한의 정리만 수행 - 원본 제목 최대한 보존
        # 1. 연속된 공백 정리만
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 2. 기자명만 제거 (예: "엄성용 기자", "한병규 기자")
        text = re.sub(r'\s*[가-힣]{2,4}\s*기자\s*$', '', text)
        
        # 3. 날짜/시간 제거 (예: "2025-10-20 16:54", "16:54", "14:17")
        text = re.sub(r'\s*\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2}\s*$', '', text)
        text = re.sub(r'\s*\d{2}:\d{2}\s*$', '', text)
        
        # 4. 최종 정리
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 5. 너무 짧거나 의미없는 제목만 제거
        if len(text) < 5 or text in ['', '...', '제목', '뉴스', '기사']:
            return ""
        
        return text
    
    def normalize_title(self, title):
        """제목 정규화 (중복 체크용)"""
        import re
        
        # 소문자 변환, 공백 정리, 특수문자 제거
        normalized = re.sub(r'[^\w\s가-힣]', '', title.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # 불필요한 단어 제거
        stop_words = ['기사', '뉴스', '보도', '발표', '시행', '실시']
        for word in stop_words:
            normalized = normalized.replace(word, '')
        
        return normalized
    
    def is_similar_title(self, title, seen_titles):
        """유사한 제목인지 확인"""
        normalized = self.normalize_title(title)
        
        for seen_title in seen_titles:
            # 80% 이상 일치하면 유사한 것으로 판단
            if self.calculate_similarity(normalized, seen_title) > 0.8:
                return True
        return False
    
    def calculate_similarity(self, text1, text2):
        """두 텍스트의 유사도 계산 (간단한 버전)"""
        if not text1 or not text2:
            return 0
        
        # 공통 단어 수 계산
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0
        
    def crawl_education_ministry(self, url, base_url):
        """교육부 뉴스 크롤링"""
        news_list = []
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 교육부 뉴스 리스트 파싱
            news_items = soup.find_all('tr', class_='board-list')
            
            for item in news_items:
                try:
                    title_elem = item.find('td', class_='title')
                    date_elem = item.find('td', class_='date')
                    link_elem = item.find('a')
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        date_text = date_elem.get_text(strip=True) if date_elem else ''
                        link = urljoin(base_url, link_elem.get('href', ''))
                        
                        # 상세 내용 크롤링
                        content = self.get_article_content(link)
                        
                        news_list.append({
                            '날짜': date_text,
                            '제목': title,
                            '내용': content,
                            '출처': '교육부',
                            '링크': link,
                            '크롤링시간': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                except Exception as e:
                    logger.error(f"교육부 뉴스 아이템 파싱 오류: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"교육부 뉴스 크롤링 오류: {e}")
            
        return news_list
    
    def crawl_general_news(self, url, base_url, source_name):
        """일반 교육 뉴스 사이트 크롤링 (개선된 버전)"""
        news_list = []
        seen_titles = set()  # 중복 체크용 제목 집합
        seen_links = set()   # 중복 체크용 링크 집합
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            logger.info(f"{source_name} 크롤링 시작 - URL: {url}")
            
            # 사이트별 특화된 파싱 로직 - 제목 태그 직접 추출
            if 'eduhope' in source_name.lower():
                # 교육희망 특화 파싱 - 제목 태그 직접 찾기
                title_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], class_=re.compile(r'title|head|subject'))
                if not title_elements:
                    # 제목 태그가 없으면 링크에서 추출
                    all_links = soup.find_all('a', href=True)
                    all_links = [link for link in all_links if link.get_text(strip=True) and len(link.get_text(strip=True)) > 10]
                else:
                    all_links = title_elements
            elif 'hangyo' in source_name.lower():
                # 한국교육신문 특화 파싱 - 더 정교하게
                # 1. 제목 태그 찾기 (더 넓은 범위)
                title_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                # 2. 클래스명으로 제목 찾기
                title_by_class = soup.find_all(['div', 'span', 'p'], class_=re.compile(r'title|head|subject|news'))
                # 3. 링크에서 제목 찾기
                link_titles = soup.find_all('a', href=True)
                
                # 모든 방법을 시도
                all_links = []
                if title_elements:
                    all_links.extend(title_elements)
                if title_by_class:
                    all_links.extend(title_by_class)
                if not all_links:
                    all_links = [link for link in link_titles if link.get_text(strip=True) and len(link.get_text(strip=True)) > 10]
            elif 'educhang' in source_name.lower():
                # 교육언론창 특화 파싱
                title_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if not title_elements:
                    all_links = soup.find_all('a', href=True)
                else:
                    all_links = title_elements
            else:
                # 일반적인 파싱 - 제목 태그 우선, 없으면 링크
                title_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if title_elements:
                    all_links = title_elements
                else:
                    all_links = soup.find_all('a', href=True)
            
            logger.info(f"{source_name}에서 총 {len(all_links)}개 링크 발견")
            
            news_count = 0
            for link in all_links:
                try:
                    text = link.get_text(strip=True)
                    
                    # 제목 태그인 경우 링크 찾기
                    if link.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        # 제목 태그 안의 링크 찾기
                        href_element = link.find('a', href=True)
                        if href_element:
                            href = href_element.get('href', '')
                        else:
                            # 제목 태그 자체에 링크가 없으면 스킵
                            continue
                    else:
                        # 일반 링크인 경우
                        href = link.get('href', '')
                    
                    # 스마트 필터로 뉴스인지 확인
                    if self.smart_filter.is_valid_news(text, href):
                        
                        # 링크 완성
                        full_link = urljoin(base_url, href)
                        
                        # 원본 텍스트 로깅 (디버깅용)
                        logger.info(f"원본 텍스트: {text[:100]}...")
                        
                        # 깔끔한 제목 추출
                        clean_title = self.extract_clean_title(text)
                        
                        # 추출된 제목 로깅 (디버깅용)
                        logger.info(f"추출된 제목: {clean_title}")
                        
                        # 제목이 너무 짧거나 의미없으면 스킵 (더 엄격하게)
                        if (len(clean_title) < 10 or 
                            clean_title in ['', '...', '제목', '뉴스', '기사'] or
                            clean_title.startswith(('http', 'www', 'mailto')) or
                            '정책' in clean_title or '책임자' in clean_title):
                            continue
                        
                        # 강화된 중복 체크 (제목 + 링크 기준)
                        title_normalized = self.normalize_title(clean_title)
                        is_duplicate = (
                            title_normalized in seen_titles or 
                            full_link in seen_links or
                            self.is_similar_title(clean_title, seen_titles)
                        )
                        
                        if not is_duplicate:
                            seen_titles.add(title_normalized)
                            seen_links.add(full_link)
                            
                            news_list.append({
                                '날짜': datetime.now().strftime('%Y-%m-%d'),
                                '제목': clean_title,
                                '출처': source_name,
                                '링크': full_link,
                                '크롤링시간': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            })
                            
                            news_count += 1
                            logger.info(f"{source_name} 뉴스 수집: {clean_title[:50]}...")
                            
                            if news_count >= 20:  # 최대 20개
                                break
                        else:
                            logger.info(f"{source_name} 중복 제외: {clean_title[:30]}...")
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"{source_name} 뉴스 크롤링 오류: {e}")
            
        logger.info(f"{source_name}에서 총 {len(news_list)}개 뉴스 수집")
        return news_list
    


    
    @log_performance
    def crawl_all_sources(self, sources: List[Dict]) -> List[Dict]:
        """모든 뉴스 소스 크롤링 (병렬 처리 개선)"""
        all_news = []
        
        # 병렬 크롤링 실행
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 각 소스별 크롤링 작업 제출
            future_to_source = {
                executor.submit(self._crawl_single_source, source): source 
                for source in sources
            }
            
            # 결과 수집
            for future in concurrent.futures.as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    news = future.result()
                    if news:
                        all_news.extend(news)
                        logger.info(f"✅ {source['name']}: {len(news)}개 뉴스 수집")
                    else:
                        logger.warning(f"⚠️ {source['name']}: 뉴스 수집 실패")
                except Exception as e:
                    error_handler.handle_error(
                        e, 
                        f"소스 크롤링 실패: {source['name']}",
                        source=source['name'],
                        url=source['url']
                    )
                    logger.error(f"❌ {source['name']} 크롤링 실패: {e}")
        
        # 성능 통계 업데이트
        self.performance_stats['total_crawled'] += len(all_news)
        self.performance_stats['successful_crawls'] += len(all_news)
        
        return all_news
    
    @error_handler.retry_on_error(max_retries=2, delay=1.0)
    def _crawl_single_source(self, source: Dict) -> List[Dict]:
        """단일 소스 크롤링 (재시도 로직 포함)"""
        logger.info(f"🔄 {source['name']} 크롤링 시작...")
        
        if '교육부' in source['name']:
            news = self.crawl_education_ministry(source['url'], source['base_url'])
        else:
            news = self.crawl_general_news(source['url'], source['base_url'], source['name'])
        
        # 스마트 필터 적용
        filtered_news = self.smart_filter.filter_news_list(news)
        logger.info(f"📊 {source['name']}: {len(news)}개 → {len(filtered_news)}개 (필터링 후)")
        
        return filtered_news
    
    def generate_content_hash(self, content: str) -> str:
        """콘텐츠 해시 생성 (중복 체크용)"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def enhanced_deduplication(self, news_list: List[Dict]) -> List[Dict]:
        """향상된 중복 제거 (제목 + 내용 해시 기반)"""
        seen_hashes = set()
        unique_news = []
        
        for news in news_list:
            # 제목과 내용을 결합한 해시 생성
            content = f"{news.get('제목', '')}{news.get('내용', '')}"
            content_hash = self.generate_content_hash(content)
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_news.append(news)
            else:
                logger.debug(f"중복 제거: {news.get('제목', '')[:30]}...")
        
        logger.info(f"중복 제거: {len(news_list)} → {len(unique_news)}개")
        return unique_news
    
    def validate_news_quality(self, news: Dict) -> bool:
        """뉴스 품질 검증"""
        # 필수 필드 확인
        required_fields = ['제목', '출처', '링크']
        for field in required_fields:
            if not news.get(field):
                return False
        
        # 제목 길이 확인 (너무 짧거나 긴 경우 제외)
        title = news.get('제목', '')
        if len(title) < 5 or len(title) > 200:
            return False
        
        # 링크 유효성 확인
        link = news.get('링크', '')
        if not link.startswith(('http://', 'https://')):
            return False
        
        return True
    
    def get_performance_stats(self) -> Dict:
        """성능 통계 반환"""
        return {
            **self.performance_stats,
            'error_stats': error_handler.get_error_stats(),
            'crawled_urls_count': len(self.crawled_urls)
        }
    
    def save_to_json(self, news_list: List[Dict], filename: str = 'education_news.json') -> bool:
        """JSON 파일로 저장 (개선된 버전)"""
        try:
            if not news_list:
                logger.warning("저장할 뉴스가 없습니다.")
                return False
            
            # 데이터 품질 검증
            valid_news = [news for news in news_list if self.validate_news_quality(news)]
            logger.info(f"품질 검증: {len(news_list)} → {len(valid_news)}개")
            
            # 중복 제거
            unique_news = self.enhanced_deduplication(valid_news)
            
            # JSON 저장
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(unique_news, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ JSON 파일 저장 완료: {filename} ({len(unique_news)}개 뉴스)")
            return True
            
        except Exception as e:
            error_handler.handle_error(e, "JSON 파일 저장 실패", url=filename)
            return False

if __name__ == "__main__":
    from config import NEWS_SOURCES
    
    crawler = EducationNewsCrawler()
    news_list = crawler.crawl_all_sources(NEWS_SOURCES)
    crawler.save_to_json(news_list)
    
    print(f"총 {len(news_list)}개의 교육 뉴스를 수집했습니다.")