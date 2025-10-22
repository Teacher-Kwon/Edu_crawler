# 설정 파일
import os

# 구글 스프레드시트 설정
GOOGLE_CREDENTIALS_FILE = 'credentials.json'  # 구글 서비스 계정 키 파일
SPREADSHEET_ID = '1B001qtMZKIEv_1DGCdwidNuiYI4-QLBZNzR5EpwyoKg' #교육 뉴스 크롤링 스프레드시트 ID
WORKSHEET_NAME = '교육 뉴스 크롤링'  # 워크시트 이름

# 크롤링 설정
NEWS_SOURCES = [

    {
        'name': '한국교육신문',
        'url': 'https://www.hangyo.com/news/articleList.html?sc_section_code=S1N1&view_type=sm',
        'base_url': 'https://www.hangyo.com'
    },
        {
        'name': '교육희망',
        'url': 'https://news.eduhope.net/sub_view.html?type=abs',
        'base_url': 'https://news.eduhope.net/'
    },        
    {
        'name': '교육언론창',
        'url': 'https://www.educhang.co.kr/news/articleList.html?page=3&total=5831&box_idxno=&view_type=sm',
        'base_url': 'https://www.educhang.co.kr/'
    },
    {
        'name': '에듀프레스',
        'url': 'https://www.edupress.kr/news/articleList.html?sc_section_code=S1N1&view_type=sm',
        'base_url': 'https://www.edupress.kr/'
    },
    {
        'name': '경향신문',
        'url': 'https://www.khan.co.kr/national/education/articles',
        'base_url': 'https:/www.khan.co.kr/'
    }
]

# 스프레드시트 컬럼 설정
COLUMNS = [
    '날짜',
    '제목', 
    '출처',
    '링크',
    '크롤링시간'
]

# 크롤링 간격 (분)
CRAWL_INTERVAL = 60  # 1시간마다 실행
