# link_helper.py
# 상품명 정제 및 최적의 제품 링크 추출 모듈

import re
import urllib.parse
from config import COUPANG_AF_ID

def clean_product_keyword(raw_title: str) -> str:
    """게시글 제목에서 쇼핑몰명, 가격 등 제거 후 핵심 키워드 추출"""
    text = re.sub(r'\[.*?\]', '', raw_title)
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'[\/_,\+~]+', ' ', text)
    words = text.split()
    if len(words) > 4:
        words = words[:4]
    keyword = ' '.join(words).strip()
    return keyword if keyword else raw_title[:30]

def make_coupang_search_url(keyword: str) -> str:
    """쿠팡 검색 결과에 파트너스 AF코드 태그 삽입"""
    encoded = urllib.parse.quote(keyword)
    return f"https://www.coupang.com/np/search?q={encoded}&channel=user&lptag={COUPANG_AF_ID}"

def get_product_link(direct_url: str, title: str) -> str:
    """
    단일 제품 링크 결정:
    1. 쿠팡 상품인 경우: AF태그가 삽입된 쿠팡 다이렉트 링크 반환
    2. 타 쇼핑몰인 경우: 실제 구매 가능한 원문 쇼핑몰 링크 반환
    """
    if direct_url and 'coupang.com' in direct_url:
        separator = '&' if '?' in direct_url else '?'
        return f"{direct_url}{separator}lptag={COUPANG_AF_ID}"
        
    if direct_url and direct_url.startswith('http'):
        return direct_url
        
    return make_coupang_search_url(clean_product_keyword(title))
