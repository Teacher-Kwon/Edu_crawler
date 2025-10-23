# 스마트 뉴스 필터링 모듈
import re

class SmartNewsFilter:
    def __init__(self):
        # 제외할 키워드들 (대폭 확장)
        self.exclude_keywords = [
            '많이 본 기사', '인기 기사', '최신 기사', '뉴스', '기사',
            '메뉴', '홈', '로그인', '회원가입', '검색', '더보기',
            '이전', '다음', '목록', '리스트', '페이지', '번호',
            '공지사항', '알림', '설정', '도움말', '고객센터',
            '사이트맵', '이용약관', '개인정보처리방침', '저작권',
            '광고', '배너', '이미지', '사진', '동영상',
            '카테고리', '분류', '태그', '키워드', '검색어',
            '전체', '전체보기', '모든', '모든기사', '전체기사',
            # 추가 제외 키워드
            '정책', '책임자', '담당자', '관리자', '운영자',
            '홈페이지', '사이트', '웹사이트', '웹페이지',
            '바로가기', '링크', 'URL', '주소', '연결',
            '팝업', '새창', '새탭', '새페이지',
            '다운로드', '업로드', '파일', '문서', 'PDF',
            '이메일', '메일', '연락처', '전화', '주소',
            '회사', '기업', '단체', '조직', '협회',
            '소개', '안내', '가이드', '매뉴얼', '설명서',
            '이벤트', '행사', '모임', '모집', '신청',
            '구독', '구독하기', '팔로우', '좋아요', '공유',
            '댓글', '답글', '리플', '트윗', '포스트',
            '프로필', '계정', '마이페이지', '내정보',
            '결제', '구매', '주문', '배송', '환불',
            '고객', '문의', '상담', '지원', '서비스'
        ]
        
        # 뉴스 제목에 포함될 만한 키워드들
        self.news_keywords = [
            '발표', '시행', '실시', '추진', '계획', '방안',
            '정책', '제도', '개선', '확대', '도입', '시작', '종료',
            '결과', '성과', '효과', '영향', '변화', '전망', '예상',
            '논의', '검토', '심의', '의결', '통과', '부결', '승인',
            '지원', '투자', '예산', '자금', '기금', '보조금', '장학금',
            '교육', '학교', '학생', '교사', '교수', '교장', '교감',
            '대학', '입시', '시험', '정책', '수업', '학원', '연구',
            '안전', '보건', '복지', '문화', '체육', '예술', '과학',
            '기술', '디지털', '온라인', '원격', '혁신', '창의',
            # 경향신문 특화 키워드
            '서울', '경기', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
            '초등', '중등', '고등', '유치원', '어린이집', '보육', '양육',
            '특수', '장애', '통합', '포용', '다문화', '이주', '외국인',
            '학점제', '고교', '대입', '수능', '내신', '성적', '평가',
            '교권', '교원', '선생님', '교장', '교감', '교사협회',
            '급식', '안전', '사고', '사망', '부상', '응급처치',
            '코로나', '감염', '방역', '마스크', '거리두기', '온라인수업'
        ]
        
        # 뉴스 제목 패턴 (정규식)
        self.news_patterns = [
            r'.*발표.*',  # 발표가 포함된 제목
            r'.*시행.*',  # 시행이 포함된 제목
            r'.*정책.*',  # 정책이 포함된 제목
            r'.*계획.*',  # 계획이 포함된 제목
            r'.*지원.*',  # 지원이 포함된 제목
            r'.*투자.*',  # 투자가 포함된 제목
            r'.*교육.*',  # 교육이 포함된 제목
            r'.*학교.*',  # 학교가 포함된 제목
            r'.*학생.*',  # 학생이 포함된 제목
            r'.*교사.*',  # 교사가 포함된 제목
            # 경향신문 특화 패턴
            r'.*서울.*교육.*',  # 서울 교육 관련
            r'.*경기.*교육.*',  # 경기 교육 관련
            r'.*특수.*학교.*',  # 특수학교 관련
            r'.*고교.*학점제.*',  # 고교학점제 관련
            r'.*교권.*',  # 교권 관련
            r'.*급식.*',  # 급식 관련
            r'.*안전.*',  # 안전 관련
            r'.*다문화.*',  # 다문화 관련
            r'.*이주.*',  # 이주 관련
            r'.*장애.*',  # 장애 관련
        ]
    
    def is_valid_news(self, text, href):
        """뉴스인지 판단 (강화된 버전)"""
        if not text or len(text) < 15:
            return False
        
        # 1. 제외 키워드 확인 (더 엄격하게)
        for keyword in self.exclude_keywords:
            if keyword in text:
                return False
        
        # 2. 불필요한 패턴 제거
        # 정책 페이지, 메뉴 링크 등
        if any(pattern in text.lower() for pattern in ['정책', '책임자', '담당자', '관리자']):
            return False
        
        # 3. 링크 패턴 확인 (더 정교하게)
        is_news_link = any(pattern in href.lower() for pattern in [
            'news', 'article', 'story', 'report', 'post', 'view', 'national', 'education'
        ])
        
        # 4. 뉴스 키워드 확인
        has_news_keyword = any(keyword in text for keyword in self.news_keywords)
        
        # 5. 뉴스 제목 패턴 확인
        matches_pattern = any(re.match(pattern, text) for pattern in self.news_patterns)
        
        # 6. 길이와 내용 품질 확인
        is_proper_length = 15 <= len(text) <= 200
        has_meaningful_content = not text.startswith(('http', 'www', 'mailto'))
        
        # 7. 최종 판단 (더 엄격한 조건)
        return (
            (has_news_keyword or is_news_link or matches_pattern) and 
            is_proper_length and 
            has_meaningful_content and
            len(text) > 15
        )
    
    def filter_news_list(self, news_list):
        """뉴스 리스트 필터링"""
        filtered_news = []
        
        for news in news_list:
            title = news.get('제목', '')
            link = news.get('링크', '')
            
            if self.is_valid_news(title, link):
                filtered_news.append(news)
            else:
                print(f"필터링 제외: {title[:30]}...")
        
        return filtered_news

# 사용 예시
if __name__ == "__main__":
    filter_tool = SmartNewsFilter()
    
    # 테스트 데이터
    test_news = [
        {'제목': '많이 본 기사', '링크': 'https://example.com'},
        {'제목': '교육부 디지털 교육 정책 발표', '링크': 'https://example.com/news/123'},
        {'제목': '학교 급식 개선 방안 논의', '링크': 'https://example.com/article/456'},
        {'제목': '메뉴', '링크': 'https://example.com/menu'},
        {'제목': '학생 안전 교육 강화 추진', '링크': 'https://example.com/news/789'},
    ]
    
    filtered = filter_tool.filter_news_list(test_news)
    
    print("필터링 결과:")
    for news in filtered:
        print(f"- {news['제목']}")
